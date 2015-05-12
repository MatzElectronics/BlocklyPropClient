__author__ = 'Michel & Vale'

import Tkinter as tk
import ttk as ttk
import tkMessageBox
import tkFileDialog
import ScrolledText
import multiprocessing
from datetime import datetime
import threading
import webbrowser
import os
import ip
import time
import BlocklyServer
from PropC_library_finder import propc_library_finder

PORT = 6009
VERSION = 0.2


class BlocklyPropClient(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # initialize values
        self.version = 0.0
        self.connected = False

        # initialize config variables
        self.ip_address = tk.StringVar()
        self.port = tk.StringVar()
        self.trace_log = tk.IntVar()

        self.trace_log.set(1)

        self.title("BlocklyProp")

        # Set icon
        if "nt" == os.name:
            self.wm_iconbitmap(bitmap='blocklyprop.ico')
        else:
            #self.wm_iconbitmap(bitmap = "@myicon.xbm")
            pass

        self.initialize()
        self.initialize_menu()

    def set_version(self, version):
        self.version = version

    def initialize(self):
        self.grid()

        self.lbl_ip_address = ttk.Label(self, anchor=tk.E, text='IP Address :')
        self.lbl_ip_address.grid(column=0, row=0, sticky='nesw')

        self.ent_ip_address = ttk.Entry(self, state='readonly', textvariable=self.ip_address)
        self.ent_ip_address.grid(column=1, row=0, sticky='nesw', padx=3, pady=3)

        self.lbl_port = ttk.Label(self, anchor=tk.E, text='Port :')
        self.lbl_port.grid(column=0, row=1, sticky='nesw')
        
        self.btn_open_browser = ttk.Button(self, text='Open Browser', command=self.handle_browser)
        self.btn_open_browser.grid(column=0, row=2, sticky='nesw', padx=3, pady=3)

        self.ent_port = ttk.Entry(self, textvariable=self.port)
        self.ent_port.grid(column=1, row=1, sticky='nesw', padx=3, pady=3)

        self.btn_connect = ttk.Button(self, text='Connect', command=self.handle_connect)
        self.btn_connect.grid(column=1, row=2, sticky='nesw', padx=3, pady=3)
        
        self.lbl_current_code = ttk.Label( self, anchor=tk.E, text='Code most recently compiled :' )
        self.lbl_current_code.grid(column=0, row=5, sticky='nesw', padx=3, pady=3)
        
        self.current_code = ScrolledText.ScrolledText( self, state='disabled')
        self.current_code.grid(column=0, row=6, columnspan=2, sticky='nesw', padx=3, pady=3)

        self.lbl_log = ttk.Label(self, anchor=tk.W, text='Log :')
        self.lbl_log.grid(column=0, row=3, sticky='nesw', padx=3, pady=3)

        self.ent_log = ScrolledText.ScrolledText(self, state='disabled')
        self.ent_log.grid(column=0, row=4, columnspan=2, sticky='nesw', padx=3, pady=3)

        #s = ttk.Style()
        #s.configure('Right.TCheckbutton', anchor='e')
        #self.check_log_trace = ttk.Checkbutton(self, style='Right.TCheckbutton', text='Trace logging', variable=self.trace_log)
        self.check_log_trace = tk.Checkbutton(self, anchor=tk.E, text='Trace logging', variable=self.trace_log, offvalue=1, onvalue=0)
        self.check_log_trace.grid(column=1, row=3, sticky='nesw', padx=3, pady=3)
        
        #self.btn_log_checkbox = ttk.Button(self, text='Low level logging: Currently False', command=self.handle_lowlevel_logging)
        #self.btn_log_checkbox.grid(column=1, row=3, sticky='nesw', padx=3, pady=3)

        self.grid_columnconfigure(0, minsize=100)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(4, weight=1)
        self.resizable(True, True)
        self.minsize(250, 200)

        self.protocol("WM_DELETE_WINDOW", self.handle_close)

        self.ip_address.set(ip.get_lan_ip())
        self.port.set(PORT)

        self.q = multiprocessing.Queue()
 #       self.stdoutToQueue = StdoutToQueue(self.q)

        monitor = threading.Thread(target=self.text_catcher)
        monitor.daemon = True
        monitor.start()
    
        code_monitor = threading.Thread( target=self.code_catcher)
        code_monitor.daemon = True
        code_monitor.start()
    
    def initialize_menu( self ):
        menubar = tk.Menu( self )

        file_menu = tk.Menu( menubar, tearoff=0 )
        file_menu.add_command( label="Save" )
        file_menu.add_command( label="Save As...", command=self.handle_save_as )
        file_menu.add_command( label="Open" )
        menubar.add_cascade( label="File", menu=file_menu )
        
        about_menu = tk.Menu( menubar, tearoff=0 )
        about_menu.add_command( label="BlocklyPropClient Source Code", command=self.handle_client_code_browser )
        about_menu.add_command( label="BlocklyProp Source Code", command=self.handle_code_browser )
        about_menu.add_separator()
        about_menu.add_command( label="About", command=self.about_info )
        menubar.add_cascade( label="About", menu=about_menu)
        
        options_menu = tk.Menu( menubar, tearoff=0 )
        options_menu.add_command( label="Set Library Location", command=self.handle_library_location )
        menubar.add_cascade( label="Options", menu=options_menu )
        
        help_menu = tk.Menu( menubar, tearoff=0 )
        help_menu.add_command( label="Help" )
        menubar.add_cascade( label="Help", menu=help_menu )
    
        self.config( menu=menubar )

    def handle_connect(self):
        if self.connected:
            BlocklyServer.stop(self.q)
            self.server_process.terminate()
            self.connected = False
            self.btn_connect['text'] = "Connect"
        else:
            # read entered values and start server
            self.server_process = multiprocessing.Process(target=BlocklyServer.main, args=(int(self.port.get()), self.version, self.q)) #, kwargs={'out':self.stdoutToQueue})
           # self.server_process = threading.Thread(target=BlocklyServer.main, args=(int(self.port.get()), self.version)) #, kwargs={'out':self.stdoutToQueue})
            self.server_process.start()

            self.connected = True
            self.btn_connect['text'] = "Disconnect"

    def handle_save_as( self ):
        file = tkFileDialog.asksaveasfile( mode='w' )
        code = open( "c_code_file", 'r' ).read()

        file.write( code )
        file.close()
    
        tkMessageBox.showinfo( "Info", "The most recently compiled code has been saved to a file successfully"  )

    def handle_browser(self):
        webbrowser.open_new( 'http://blocklyprop.creatingfuture.eu' )
    
    def handle_code_browser( self ):
        webbrowser.open_new( 'http://github.com/parallaxinc/BlocklyProp' )
    
    def handle_client_code_browser( self ):
        webbrowser.open_new( 'http://github.com/parallaxinc/BlocklyPropClient' )
    
    def handle_library_location( self ):
        library_finder = propc_library_finder()
            
        tkMessageBox.showinfo( "Info", "Library Location Set To: " + library_finder.get_directory() )
    
    def about_info( self ):
        tkMessageBox.showinfo( "About BlocklyProp", "CurrentVersion: v0.2.0\n\nAuthors: Vale Tolpegin & Michel Lampo\n\nRepository Source Code: http://github.com/parallaxinc/BlocklyPropClient\n\nCopyright 2015 Parallax Inc" )

    def handle_close(self):
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            # stop server if running
            if self.connected:
               # BlocklyServer.stop()
                self.server_process.terminate()
            self.quit()

    def code_catcher( self ):
        while 1:
            try:
                code = open( "c_code_file", 'r' ).read()
            except:
                code = ""

            self.current_code['state'] = 'normal'
            self.current_code.delete( "1.0", tk.END )
            self.current_code.insert( "1.0", code )
            self.current_code['state'] = 'disabled'

            time.sleep( 2 )

    def text_catcher(self):
        while 1:
            (level, level_name, message) = self.q.get()
            min_level = self.trace_log.get() * 5
            if level > min_level:
                self.ent_log['state'] = 'normal'
                self.ent_log.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + level_name + ': ' + message + '\n')
                self.ent_log.yview_pickplace("end")
                self.ent_log['state'] = 'disabled'


if __name__ == '__main__':
    multiprocessing.freeze_support()

    bp_client = BlocklyPropClient()
    bp_client.set_version(VERSION)
    bp_client.mainloop()