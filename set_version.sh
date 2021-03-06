#!/bin/sh --
#
# This script sets version number entries in various files in the BlocklyPropClient project.
# Works in Ubuntu and OS X.
#
# Usage: $ ./set_version "1.2.3"


#
# Error if no version string declared
#
# if [ $1X == X ]     <-- this doesn't work in Ubuntu
if [ -z "$1" ]
then
    echo "ERROR: Must specify a version number.  Ex: \$ $0 \"1.2.3\""
    exit 1
fi


#
# Get version string
#
VERSION=$1


#
# FindAndSetVersion function
#   Find and update version string in form "Version = #.#.#" 
#   Search is: case-insensitive, space, tabs, or nothing around '=', and one or more # in each placeholder.
#   Replace is: performed in-place inside of file; however, a backup (.bak) of the original file is also made.  
#
# NOTE: sed on Mac doesn't include a case-insensitive option.  To keep the search pattern equivalent for both
#       grep and sed, must use an expanded pattern for text where each letter is expressed in both upper/lower case.
#       ex: Ver should be [vV][eE][rR]  
#
# function FindAndSetVersion {     <-- this doesn't work in Ubuntu
FindAndSetVersion() {
if grep -q -E ${VERSIONPATTERN} ${VERSIONFILE} ; then
    if sed -i.bak -E "s/${VERSIONPATTERN}/${VERSIONSTRING}/" ${VERSIONFILE} ; then
        echo "Updated file \"${VERSIONFILE}\" to include: ${VERSIONSTRING}"
    fi
else
    echo "ERROR: Unable to find version string in file \"${VERSIONFILE}\""
fi
}


#
# Adjust BlocklyPropClient.py file - [format: VERSION = "#.#.#"]
#
VERSIONFILE=BlocklyPropClient.py
VERSIONPATTERN=[vV][eE][rR][sS][iI][oO][nN][[:blank:]]*=[[:blank:]]*\"[0-9]+\.[0-9]+\.[0-9]+\"
VERSIONSTRING="VERSION = \"${VERSION}\""

FindAndSetVersion


#
# Adjust about.txt file - [format: Version: v#.#.#]
#
VERSIONFILE=about.txt
VERSIONPATTERN=[vV][eE][rR][sS][iI][oO][nN]:[[:blank:]]*v[[:blank:]]*[0-9]+\.[0-9]+\.[0-9]+
VERSIONSTRING="Version: v${VERSION}"

FindAndSetVersion


#
# Adjust package/blocklypropclient-installer.iss file - [format: MyAppVersion "#.#.#"]
#
VERSIONFILE=package/blocklypropclient-installer.iss
VERSIONPATTERN=[mM][yY][aA][pP][pP][vV][eE][rR][sS][iI][oO][nN][[:blank:]]+\"[0-9]+\.[0-9]+\.[0-9]+\"
VERSIONSTRING="MyAppVersion \"${VERSION}\""

FindAndSetVersion
