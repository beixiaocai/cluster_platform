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

    path('node/index', NodeView.index),
    path('node/openDel', NodeView.api_openDel),
    path('node/getOnlineNodes', NodeView.api_getOnlineNodes),

    path('alarm/index', AlarmView.index),
    path('alarm/openHandle', AlarmView.api_openHandle),
    path('alarm/openExport', AlarmView.api_openExport),
    path('alarm/openIndex', AlarmView.api_openIndex),
    path('alarm/openInfo', AlarmView.api_openInfo),
    path('alarm/openContext', AlarmView.api_openContext),
    path('alarm/openEdit', AlarmView.api_openEdit),


    path('stream/index', StreamView.index),
    path('stream/getNodeStreams', StreamView.api_getNodeStreams),
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
    path('control/openAddAlgorithm', ControlView.api_openAddAlgorithm),
    path('control/openEditAlgorithm', ControlView.api_openEditAlgorithm),
    path('control/openDelAlgorithm', ControlView.api_openDelAlgorithm),
    path('control/openStartControlStream', ControlView.api_openStartControlStream),
    path('control/openStopControlStream', ControlView.api_openStopControlStream),

    path('inner/on_stream_not_found', InnerlView.api_on_stream_not_found),

    path('open/getIndex', OpenView.api_getIndex),
    path('open/getNodeList', OpenView.api_getNodeList),
    path('open/getZlmProcessData', OpenView.api_getZlmProcessData),
    path('open/getAllCoreProcessData', OpenView.api_getAllCoreProcessData),
    path('open/getAllCoreProcessData2', OpenView.api_getAllCoreProcessData2),
    path('open/getAllStreamData', OpenView.api_getAllStreamData),
    path('open/getControl', OpenView.api_getControl),
    path('open/restartApp', OpenView.api_restartApp),
    path('open/restartOS', OpenView.api_restartOS),

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
    path('alarmInterface/openTest', AlarmInterfaceView.api_openTest),

    path('algorithmFlow/index', AlgorithmFlowView.index),
    path('algorithmFlow/getList', AlgorithmFlowView.api_getList),
    path('algorithmFlow/getInfo', AlgorithmFlowView.api_getInfo),
    path('algorithmFlow/openEdit', AlgorithmFlowView.api_openEdit),
    path('algorithmFlow/openDel', AlgorithmFlowView.api_openDel),

    path('algorithm/index', AlgorithmView.index),
    path('algorithm/getList', AlgorithmView.api_getList),
    path('algorithm/getInfo', AlgorithmView.api_getInfo),
    path('algorithm/openEdit', AlgorithmView.api_openEdit),
    path('algorithm/openDel', AlgorithmView.api_openDel),

    path('behaviour/index', BehaviourView.index),
    path('behaviour/getList', BehaviourView.api_getList),
    path('behaviour/getInfo', BehaviourView.api_getInfo),
    path('behaviour/openEdit', BehaviourView.api_openEdit),
    path('behaviour/openDel', BehaviourView.api_openDel),
]
