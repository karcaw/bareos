from bareosdir import *
from bareos_dir_consts import *

def load_bareos_plugin(context):
  DebugMessage(context, 100, "load_bareos_plugin called\n");
  events = [];
  events.append(bDirEventType['bDirEventJobStart']);
  events.append(bDirEventType['bDirEventJobEnd']);
  events.append(bDirEventType['bDirEventJobInit']);
  events.append(bDirEventType['bDirEventJobRun']);
  RegisterEvents(context, events);
  return bRCs['bRC_OK'];

def handle_plugin_event(context, event):
  if event == bDirEventType['bDirEventJobStart']:
    DebugMessage(context, 100, "bDirEventJobStart event triggered\n");
    jobname = GetValue(context, brDirVariable['bDirVarJobName']);
    DebugMessage(context, 100, "Job " + jobname + " starting\n");

  elif event == bDirEventType['bDirEventJobEnd']:
    DebugMessage(context, 100, "bDirEventJobEnd event triggered\n");
    jobname = GetValue(context, brDirVariable['bDirVarJobName']);
    DebugMessage(context, 100, "Job " + jobname + " stopped\n");

  elif event == bDirEventType['bDirEventJobInit']:
    DebugMessage(context, 100, "bDirEventJobInit event triggered\n");

  elif event == bDirEventType['bDirEventJobRun']:
    DebugMessage(context, 100, "bDirEventJobRun event triggered\n");

  return bRCs['bRC_OK'];

