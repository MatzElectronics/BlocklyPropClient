# -*- mode: python -*-
a = Analysis(['BlocklyPropClient.py'],

             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='BlocklyPropClient.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='blocklyprop.ico' )
propeller_libs_and_tools = Tree('propeller-tools', prefix='propeller-tools', excludes=['*.pdf', 'linux', 'mac'])
propeller_libs_and_tools += [('blocklyprop.ico', 'blocklyprop.ico', 'Windows icon')]
#propeller_libs_and_tools += [('blocklyprop.png', 'blocklyprop.png', 'Windows icon')]
propeller_libs_and_tools += [('about.txt', 'about.txt', 'About file')]
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               propeller_libs_and_tools,
               strip=None,
               upx=True,
               name='BlocklyPropClient.windows')

# Analysis
#             pathex=['D:\\Development\\python\\BlocklyPropClient'],
