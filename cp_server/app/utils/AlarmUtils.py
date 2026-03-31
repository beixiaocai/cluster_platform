import os
import shutil
import json
import base64
import io
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class AlarmUtils():
    def __init__(self, logger, database, storageDir):
        self.logger = logger
        self.database = database
        self.storageDir = storageDir

    def export_labelme(self, alarm_id, control_code, image_path, out_dir):
        ret = False
        msg = "未知错误"

        try:
            image_filepath = os.path.join(self.storageDir, image_path)
            alarm_id_dir = os.path.dirname(image_filepath)

            annotation_name = "%s_%d" % (control_code, alarm_id)
            annotation_filepath = os.path.join(alarm_id_dir, "%s.json" % annotation_name)

            if not os.path.exists(image_filepath):
                raise FileNotFoundError(f"image_filepath not found: {image_filepath}")

            if not os.path.exists(annotation_filepath):
                raise FileNotFoundError(f"annotation_filepath not found: {annotation_filepath}")

            if PIL_AVAILABLE:
                with Image.open(image_filepath) as img:
                    width, height = img.size

                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    image_data = base64.b64encode(img_byte_arr).decode('utf-8')
            else:
                width, height = 640, 480
                image_data = ""

            out_filename = annotation_name

            labelme_data = {
                "version": "5.5.0",
                "flags": {},
                "shapes": [],
                "imagePath": out_filename + ".jpg",
                "imageData": image_data,
                "imageHeight": height,
                "imageWidth": width
            }

            annotation_data = None
            for encoding in ["utf-8", "gbk"]:
                try:
                    f = open(annotation_filepath, 'r', encoding=encoding)
                    content = f.read()
                    annotation_data = json.loads(content)
                    f.close()
                    break
                except Exception as e:
                    pass

            if annotation_data:
                image_count = annotation_data.get("image_count", 0)
                image_detects = annotation_data.get("image_detects", [])
                if len(image_detects) == image_count:
                    detects = image_detects[0]
                    for detect in detects:
                        x1 = int(detect["x1"])
                        x2 = int(detect["x2"])
                        y1 = int(detect["y1"])
                        y2 = int(detect["y2"])
                        label = detect["class_name"]
                        if x1 >= 0 and y1 >= 0 and x2 <= width and y2 <= height:
                            shape = {
                                "label": str(label),
                                "points": [[x1, y1], [x2, y2]],
                                "group_id": None,
                                "shape_type": "rectangle",
                                "flags": {}
                            }
                            labelme_data["shapes"].append(shape)

            os.makedirs(out_dir, exist_ok=True)
            out_image_filepath = os.path.join(out_dir, out_filename + ".jpg")
            out_json_filepath = os.path.join(out_dir, out_filename + ".json")

            with open(out_json_filepath, 'w', encoding='utf-8') as f:
                json.dump(labelme_data, f, indent=2, ensure_ascii=False)

            if os.path.exists(image_filepath):
                shutil.copyfile(image_filepath, out_image_filepath)

            ret = True
            msg = "success"

        except Exception as e:
            msg = str(e)
            self.logger.error("AlarmUtils.export_labelme() error: %s" % str(e))

        return ret, msg

    def clearAlarmFiles(self, media_path, clear_type=0):
        """
        清除报警文件
        
        Args:
            media_path: 媒体文件路径（相对路径）
            clear_type: 清除类型
                0 = 删除整个报警目录（包括视频和图片）
                1 = 只删除非 mp4 文件
        
        Returns:
            bool: 是否成功删除
        """
        self.logger.info("AlarmUtils.clearAlarmFiles() media_path=%s,clear_type=%d" % (media_path, clear_type))
        
        try:
            # 验证路径格式
            if not media_path or not media_path.startswith("alarm/"):
                raise Exception("media_path=%s format error, must start with 'alarm/'" % media_path)
            
            # 构建绝对路径
            media_path_abs = os.path.join(self.storageDir, media_path)
            
            if not os.path.exists(media_path_abs):
                self.logger.warning("media_path_abs=%s does not exist, skip deletion" % media_path_abs)
                return True  # 文件不存在视为成功
            
            if clear_type == 0:
                # 删除整个报警目录（向上两级）
                file_path_parent_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(media_path_abs)))
                
                if not os.path.exists(file_path_parent_parent_dir):
                    self.logger.warning("parent directory=%s does not exist, skip deletion" % file_path_parent_parent_dir)
                    return True
                
                # 检查是否是合法的 alarm 目录结构
                if not file_path_parent_parent_dir.startswith(os.path.join(self.storageDir, "alarm")):
                    raise Exception("Invalid alarm directory structure")
                
                # 获取要删除的文件列表（用于日志）
                deleted_files = []
                for root, dirs, files in os.walk(file_path_parent_parent_dir):
                    for file in files:
                        deleted_files.append(os.path.join(root, file))
                
                # 执行删除
                shutil.rmtree(file_path_parent_parent_dir)
                
                self.logger.info("Successfully deleted %d files from directory: %s" % (
                    len(deleted_files), file_path_parent_parent_dir))
                
                # 验证删除结果
                if os.path.exists(file_path_parent_parent_dir):
                    raise Exception("Directory still exists after deletion")
                
                return True
                
            elif clear_type == 1:
                # 只删除非 mp4 文件
                file_path_parent_dir = os.path.dirname(os.path.abspath(media_path_abs))
                
                if not os.path.exists(file_path_parent_dir):
                    self.logger.warning("directory=%s does not exist, skip deletion" % file_path_parent_dir)
                    return True
                
                deleted_count = 0
                filenames = os.listdir(file_path_parent_dir)
                for __filename in filenames:
                    __filename = str(__filename)
                    if not __filename.endswith(".mp4"):
                        __filepath = os.path.join(file_path_parent_dir, __filename)
                        if os.path.exists(__filepath):
                            os.remove(__filepath)
                            deleted_count += 1
                            self.logger.debug("Deleted file: %s" % __filepath)
                
                self.logger.info("Successfully deleted %d non-mp4 files from directory: %s" % (
                    deleted_count, file_path_parent_dir))
                return True
            else:
                raise Exception("Unsupported clear_type=%d, only 0 and 1 are supported" % clear_type)
                
        except Exception as e:
            self.logger.error("AlarmUtils.clearAlarmFiles() error: %s" % str(e))
            return False

    def clearAlarm(self):
        ret = False
        msg = "未知错误"
        data = self.database.select("select video_count,video_path,image_count,image_path from cp_platform_alarm where state=5")
        if len(data) > 0:
            self.database.execute("delete from cp_platform_alarm where state=5")
            for d in data:
                video_count = d["video_count"]
                video_path = d["video_path"]
                image_count = d["image_count"]
                image_path = d["image_path"]

                if image_count > 0:
                    self.clearAlarmFiles(image_path, 0)
                elif video_count > 0:
                    self.clearAlarmFiles(video_path, 0)
            msg = "清理报警缓存成功"
            ret = True
        else:
            msg = "暂无待清理缓存"

        return ret, msg
