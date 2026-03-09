from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        from app.utils.NodeManager import g_node_manager
        g_node_manager.start_heartbeat_checker()
        g_node_manager.reset_all_nodes_offline()
