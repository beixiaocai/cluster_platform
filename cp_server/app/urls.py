from django.urls import path
from .views import UserView
from .views import IndexView
from .views import NodeView
from .views import AlarmView
from .views import StreamView
from .views import ControlView
from .views import OpenView
from .views import StorageView
from .views import SystemView
from .views import InnerlView
from .views import AudioView
from .views import AlarmInterfaceView
from .views import AlgorithmFlowView
from .views import AlgorithmView
from .views import BehaviourView
from .views import StreamRecordView
from .views import LLMView
from .views import AlgorithmTestView
from .views import FaceView
from .views import ScheduleTaskView
from .views import PlatformAlarmView

app_name = 'app'

urlpatterns = [
    path('', IndexView.index),

    path('captcha', UserView.captcha),
    path('login', UserView.login),
    path('logout', UserView.logout),

    path('user/index', UserView.index),
    path('user/add', UserView.add),
    path('user/edit', UserView.edit),
    path('user/postDel', UserView.api_postDel),
    path('user/api_openUserDetail', UserView.api_openUserDetail),

    path('platform/node/index', NodeView.index),
    path('platform/node/edit', NodeView.edit),
    path('platform/node/openDel', NodeView.api_openDel),
    path('platform/node/getOnlineNodes', NodeView.api_getOnlineNodes),
    path('platform/node/getList', NodeView.api_getList),
    path('platform/node/upgrade', NodeView.api_upgradeVersion),
    path('platform/node/restartApp', NodeView.api_restartApp),
    path('platform/node/restartOS', NodeView.api_restartOS),
    path('platform/node/exportLogs', NodeView.api_exportLogs),
    path('platform/node/downloadLog', NodeView.api_downloadLog),
    path('platform/node/getHeartbeats', NodeView.api_getHeartbeats),

    path('alarm/index', AlarmView.index),
    path('alarm/openHandle', AlarmView.api_openHandle),
    path('alarm/openExport', AlarmView.api_openExport),
    path('alarm/openIndex', AlarmView.api_openIndex),
    path('alarm/openInfo', AlarmView.api_openInfo),
    path('alarm/openContext', AlarmView.api_openContext),
    path('alarm/openEdit', AlarmView.api_openEdit),

    path('platform/alarm/index', PlatformAlarmView.index),
    path('platform/alarm/edit', PlatformAlarmView.edit),
    path('platform/alarm/openHandle', PlatformAlarmView.api_openHandle),
    path('platform/alarm/openExport', PlatformAlarmView.api_openExport),
    path('platform/alarm/openIndex', PlatformAlarmView.api_openIndex),
    path('platform/alarm/openInfo', PlatformAlarmView.api_openInfo),
    path('platform/alarm/openEdit', PlatformAlarmView.edit),
    path('platform/alarm/openAdd', PlatformAlarmView.api_openAdd),


    path('stream/index', StreamView.index),
    path('stream/getNodeStreams', StreamView.api_getNodeStreams),
    path('stream/getAllStreamData', StreamView.api_getAllStreamData),
    path('stream/openAddContext', StreamView.api_openAddContext),
    path('stream/openAdd', StreamView.api_openAdd),
    path('stream/openEditContext', StreamView.api_openEditContext),
    path('stream/openEdit', StreamView.api_openEdit),
    path('stream/openDel', StreamView.api_openDel),
    path('stream/openAddStreamProxy', StreamView.api_openAddStreamProxy),
    path('stream/openDelStreamProxy', StreamView.api_openDelStreamProxy),
    path('stream/openHandleAllStreamProxy', StreamView.api_openHandleAllStreamProxy),
    path('stream/openCheckDevice', StreamView.api_openCheckDevice),
    path('stream/openPtz', StreamView.api_openPtz),
    path('stream/openStartPusher', StreamView.api_openStartPusher),
    path('stream/openStopPusher', StreamView.api_openStopPusher),
    path('stream/player', StreamView.player),

    path('control/index', ControlView.index),
    path('control/getNodeControls', ControlView.api_getNodeControls),
    path('control/openAddContext', ControlView.api_openAddContext),
    path('control/openAdd', ControlView.api_openAdd),
    path('control/openEditContext', ControlView.api_openEditContext),
    path('control/openEdit', ControlView.api_openEdit),
    path('control/openLog', ControlView.api_openLog),
    path('control/openDel', ControlView.api_openDel),
    path('control/openHandle', ControlView.api_openHandle),
    path('control/getControlInfo', ControlView.api_getControlInfo),
    path('control/openAddAlgorithm', ControlView.api_openAddAlgorithm),
    path('control/openEditAlgorithm', ControlView.api_openEditAlgorithm),
    path('control/openDelAlgorithm', ControlView.api_openDelAlgorithm),
    path('control/openStartControlStream', ControlView.api_openStartControlStream),
    path('control/openStopControlStream', ControlView.api_openStopControlStream),
    path('control/openCopy', ControlView.api_openCopy),
    path('control/openSettings', ControlView.api_openSettings),
    path('control/openInfo', ControlView.api_openInfo),

    path('controlAlgorithm/add', ControlView.control_algorithm_add),
    path('controlAlgorithm/edit', ControlView.control_algorithm_edit),
    path('controlAlgorithm/openDel', ControlView.api_openDelAlgorithm),

    path('inner/on_stream_not_found', InnerlView.api_on_stream_not_found),

    path('index/getIndex', IndexView.api_getIndex),
    path('open/getNodeList', OpenView.api_getNodeList),
    path('open/getZlmProcessData', OpenView.api_getZlmProcessData),

    path('storage/download', StorageView.download),
    path('storage/access', StorageView.access),
    path('storage/info', StorageView.info),
    path('storage/openAccess', StorageView.openAccess),

    path('system/config', SystemView.settings),
    path('system/onlineStreams', SystemView.onlineStreams),
    path('system/getOnlineStreams', SystemView.api_getOnlineStreams),
    path('system/postExportLogs', SystemView.api_postExportLogs),
    path('system/postSaveSettings', SystemView.api_postSaveSettings),

    path('audio/index', AudioView.index),
    path('audio/getNodeAudios', AudioView.api_getNodeAudios),
    path('audio/openAdd', AudioView.api_openAdd),
    path('audio/openEdit', AudioView.api_openEdit),
    path('audio/openDel', AudioView.api_openDel),
    path('audio/openInfo', AudioView.api_openInfo),

    path('alarmInterface/index', AlarmInterfaceView.index),
    path('alarmInterface/getNodeAlarmInterfaces', AlarmInterfaceView.api_getNodeAlarmInterfaces),
    path('alarmInterface/openAdd', AlarmInterfaceView.api_openAdd),
    path('alarmInterface/openEdit', AlarmInterfaceView.api_openEdit),
    path('alarmInterface/openDel', AlarmInterfaceView.api_openDel),
    path('alarmInterface/openInfo', AlarmInterfaceView.api_openInfo),
    path('alarmInterface/test', AlarmInterfaceView.test),
    path('alarmInterface/openTest', AlarmInterfaceView.api_openTest),

    path('algorithmFlow/index', AlgorithmFlowView.index),
    path('algorithmFlow/getList', AlgorithmFlowView.api_getList),
    path('algorithmFlow/getInfo', AlgorithmFlowView.api_getInfo),
    path('algorithmFlow/openEdit', AlgorithmFlowView.api_openEdit),
    path('algorithmFlow/openDel', AlgorithmFlowView.api_openDel),
    path('algorithmFlow/openAdd', AlgorithmFlowView.api_openAdd),
    path('algorithmFlow/openEditContext', AlgorithmFlowView.api_openEditContext),
    path('algorithmFlow/openAddContext', AlgorithmFlowView.api_openAddContext),

    path('algorithm/index', AlgorithmView.index),
    path('algorithm/getList', AlgorithmView.api_getList),
    path('algorithm/getInfo', AlgorithmView.api_getInfo),
    path('algorithm/openEdit', AlgorithmView.api_openEdit),
    path('algorithm/openDel', AlgorithmView.api_openDel),
    path('algorithm/openEditContext', AlgorithmView.api_openEditContext),
    path('algorithm/openAlgorithmTypeAttrs', AlgorithmView.api_openTypeAttrs),
    path('algorithm/openAdd', AlgorithmView.api_openAdd),
    path('algorithm/openAddContext', AlgorithmView.api_openAddContext),

    path('behaviour/index', BehaviourView.index),
    path('behaviour/getList', BehaviourView.api_getList),
    path('behaviour/getInfo', BehaviourView.api_getInfo),
    path('behaviour/openEdit', BehaviourView.api_openEdit),
    path('behaviour/openDel', BehaviourView.api_openDel),
    path('behaviour/openAdd', BehaviourView.api_openAdd),
    path('behaviour/openEditContext', BehaviourView.api_openEditContext),

    path('streamRecord/index', StreamRecordView.index),
    path('streamRecord/timeplayer', StreamRecordView.timeplayer),
    path('streamRecord/getList', StreamRecordView.api_getList),
    path('streamRecord/getInfo', StreamRecordView.api_getInfo),
    path('streamRecord/getStreams', StreamRecordView.api_getStreams),
    path('streamRecord/add', StreamRecordView.api_add),
    path('streamRecord/edit', StreamRecordView.api_edit),
    path('streamRecord/del', StreamRecordView.api_del),
    path('streamRecord/getRecordTimeline', StreamRecordView.api_getRecordTimeline),
    path('streamRecord/getRecordFilename', StreamRecordView.api_getRecordFilename),
    
    path('llm/index', LLMView.index),
    path('llm/test', LLMView.test),
    path('llm/getList', LLMView.api_getList),
    path('llm/getInfo', LLMView.api_getInfo),
    path('llm/getTypes', LLMView.api_getTypes),
    path('llm/add', LLMView.api_add),
    path('llm/edit', LLMView.api_edit),
    path('llm/del', LLMView.api_del),
    path('llm/doTest', LLMView.api_test),
    
    path('algorithmTest/index', AlgorithmTestView.index),
    path('algorithmTest/getFlows', AlgorithmTestView.api_getFlows),
    path('algorithmTest/flowInit', AlgorithmTestView.api_flowInit),
    path('algorithmTest/flowRelease', AlgorithmTestView.api_flowRelease),
    path('algorithmTest/flowAnalyze', AlgorithmTestView.api_flowAnalyze),
    path('algorithmTest/getImage', AlgorithmTestView.api_getImage),
    
    path('face/index', FaceView.index),
    path('face/getNodeFaces', FaceView.api_getNodeFaces),
    path('face/openAddContext', FaceView.api_openAddContext),
    path('face/openEditContext', FaceView.api_openEditContext),
    path('face/openAdd', FaceView.api_openAdd),
    path('face/openEdit', FaceView.api_openEdit),
    path('face/openDel', FaceView.api_openDel),
    path('face/openFlows', FaceView.api_openFlows),
    path('face/openFaceDbUpdate', FaceView.api_openFaceDbUpdate),
    path('face/openFaceDbInfo', FaceView.api_openFaceDbInfo),
    path('face/openFaceDbRecognize', FaceView.api_openFaceDbRecognize),
    
    path('scheduleTask/index', ScheduleTaskView.index),
    path('scheduleTask/openIndex', ScheduleTaskView.api_openIndex),
    path('scheduleTask/openAddContext', ScheduleTaskView.api_openAddContext),
    path('scheduleTask/openEditContext', ScheduleTaskView.api_openEditContext),
    path('scheduleTask/openAdd', ScheduleTaskView.api_openAdd),
    path('scheduleTask/openEdit', ScheduleTaskView.api_openEdit),
    path('scheduleTask/openDel', ScheduleTaskView.api_openDel),
    path('scheduleTask/openToggleState', ScheduleTaskView.api_openToggleState),
    path('scheduleTask/openRunNow', ScheduleTaskView.api_openRunNow),
    path('scheduleTask/openLogs', ScheduleTaskView.api_openLogs),
]
