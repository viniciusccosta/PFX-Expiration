#define MyAppName "PFX Expiration"
#define MyAppVersion "0.2.0"
#define MyOutputBaseFilename "pfx-expiration_v0.2.0_win64"
#define MyAppPublisher "Vinícius Costa"
#define MyAppURL "https://github.com/viniciusccosta"
#define MyAppExeName "PFX Expiration.exe"
#define MyAppId GetEnv('PFX_EXPIRATION_ID')

[Setup]
AppId={{#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=C:\Users\vinic\VSCodeProjects\PFX-Expiration\LICENSE.md
OutputDir=C:\Users\vinic\VSCodeProjects\PFX-Expiration\compiler
OutputBaseFilename={#MyOutputBaseFilename}
SetupIconFile=C:\Users\vinic\VSCodeProjects\PFX-Expiration\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\vinic\VSCodeProjects\PFX-Expiration\dist\app\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\vinic\VSCodeProjects\PFX-Expiration\dist\app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

