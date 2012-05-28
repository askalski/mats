
# generated from
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066%28v=vs.85%29.aspx
# and WinUser.h
# with happy python script

eventNameToInt = {	
	"EVENT_MIN" : 0x00000001,
	"EVENT_SYSTEM_SOUND" : 0x0001,
	"EVENT_SYSTEM_ALERT" : 0x0002,
	"EVENT_SYSTEM_FOREGROUND" : 0x0003,
	"EVENT_SYSTEM_MENUSTART" : 0x0004,
	"EVENT_SYSTEM_MENUEND" : 0x0005,
	"EVENT_SYSTEM_MENUPOPUPSTART" : 0x0006,
	"EVENT_SYSTEM_MENUPOPUPEND" : 0x0007,
	"EVENT_SYSTEM_CAPTURESTART" : 0x0008,
	"EVENT_SYSTEM_CAPTUREEND" : 0x0009,
	"EVENT_SYSTEM_MOVESIZESTART" : 0x000A,
	"EVENT_SYSTEM_MOVESIZEEND" : 0x000B,
	"EVENT_SYSTEM_CONTEXTHELPSTART" : 0x000C,
	"EVENT_SYSTEM_CONTEXTHELPEND" : 0x000D,
	"EVENT_SYSTEM_DRAGDROPSTART" : 0x000E,
	"EVENT_SYSTEM_DRAGDROPEND" : 0x000F,
	"EVENT_SYSTEM_DIALOGSTART" : 0x0010,
	"EVENT_SYSTEM_DIALOGEND" : 0x0011,
	"EVENT_SYSTEM_SCROLLINGSTART" : 0x0012,
	"EVENT_SYSTEM_SCROLLINGEND" : 0x0013,
	"EVENT_SYSTEM_SWITCHSTART" : 0x0014,
	"EVENT_SYSTEM_SWITCHEND" : 0x0015,
	"EVENT_SYSTEM_MINIMIZESTART" : 0x0016,
	"EVENT_SYSTEM_MINIMIZEEND" : 0x0017,
	"EVENT_SYSTEM_DESKTOPSWITCH" : 0x0020,
	"EVENT_SYSTEM_END" : 0x00FF,
	"EVENT_OEM_DEFINED_START" : 0x0101,
	"EVENT_OEM_DEFINED_END" : 0x01FF,
	"EVENT_UIA_EVENTID_START" : 0x4E00,
	"EVENT_UIA_EVENTID_END" : 0x4EFF,
	"EVENT_UIA_PROPID_START" : 0x7500,
	"EVENT_UIA_PROPID_END" : 0x75FF,
	"EVENT_MAX" : 0x7FFFFFFF,
	"EVENT_OBJECT_CREATE" : 0x8000,
	"EVENT_OBJECT_DESTROY" : 0x8001,
	"EVENT_OBJECT_SHOW" : 0x8002,
	"EVENT_OBJECT_HIDE" : 0x8003,
	"EVENT_OBJECT_REORDER" : 0x8004,
	"EVENT_OBJECT_FOCUS" : 0x8005,
	"EVENT_OBJECT_SELECTION" : 0x8006,
	"EVENT_OBJECT_SELECTIONADD" : 0x8007,
	"EVENT_OBJECT_SELECTIONREMOVE" : 0x8008,
	"EVENT_OBJECT_SELECTIONWITHIN" : 0x8009,
	"EVENT_OBJECT_STATECHANGE" : 0x800A,
	"EVENT_OBJECT_LOCATIONCHANGE" : 0x800B,
	"EVENT_OBJECT_NAMECHANGE" : 0x800C,
	"EVENT_OBJECT_DESCRIPTIONCHANGE" : 0x800D,
	"EVENT_OBJECT_VALUECHANGE" : 0x800E,
	"EVENT_OBJECT_PARENTCHANGE" : 0x800F,
	"EVENT_OBJECT_HELPCHANGE" : 0x8010,
	"EVENT_OBJECT_DEFACTIONCHANGE" : 0x8011,
	"EVENT_OBJECT_ACCELERATORCHANGE" : 0x8012,
	"EVENT_OBJECT_INVOKED" : 0x8013,
	"EVENT_OBJECT_TEXTSELECTIONCHANGED" : 0x8014,
	"EVENT_OBJECT_CONTENTSCROLLED" : 0x8015,
	"EVENT_SYSTEM_ARRANGMENTPREVIEW" : 0x8016,
	"EVENT_OBJECT_END" : 0x80FF,
	"EVENT_AIA_START" : 0xA000,
	"EVENT_AIA_END" : 0xAFFF,
}

eventIntToName = {v : k for k, v in eventNameToInt.items()}

WINEVENT_OUTOFCONTEXT = 0x0000
WINEVENT_INCONTEXT = 0x0004
# there are two more towards threading here:
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd373640%28v=vs.85%29.aspx

CHILDID_SELF = 0


S_OK = 0
S_FALSE = 1