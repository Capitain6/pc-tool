[Setup]
AppName=PC Tool
AppVersion=4.0
AppPublisher=PC Tool
AppPublisherURL=
DefaultDirName={autopf}\PCTool
DefaultGroupName=PC Tool
OutputDir=Output
OutputBaseFilename=PCTool_Setup
SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\PCTool.exe
PrivilegesRequired=admin
VersionInfoVersion=4.0.0.0
VersionInfoDescription=PC Tool - Outil d'entretien informatique
VersionInfoCopyright=PC Tool v4.0

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon";     Description: "Creer un raccourci sur le Bureau";       GroupDescription: "Raccourcis :"; Flags: checkedonce
Name: "startupicon";     Description: "Lancer PC Tool au demarrage de Windows";  GroupDescription: "Options :";    Flags: unchecked
Name: "quicklaunchicon"; Description: "Epingler dans la barre des taches";       GroupDescription: "Raccourcis :"; Flags: unchecked

[Files]
Source: "dist\PCTool.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico";         DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PC Tool";                    Filename: "{app}\PCTool.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Desinstaller PC Tool";       Filename: "{uninstallexe}"
Name: "{commondesktop}\PC Tool";            Filename: "{app}\PCTool.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{userstartup}\PC Tool";              Filename: "{app}\PCTool.exe"; Tasks: startupicon

[Run]
Filename: "{app}\PCTool.exe"; Description: "Lancer PC Tool maintenant"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\PCTool"
