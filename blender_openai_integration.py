"""
Blender + OpenAI Integration
ربط Blender مع OpenAI ChatGPT

الميزات:
- إنشاء أكائن Blender بأوامر طبيعية
- معالجة الأوامر بواسطة GPT-4
- واجهة رسومية في Blender
"""

import bpy
import json
import os
from datetime import datetime

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


class OpenAIConfig:
    """إعدادات OpenAI"""
    API_KEY = "sk-your-api-key-here"  # استبدل بـ API Key الخاص بك
    BASE_URL = "https://api.openai.com/v1"
    MODEL = "gpt-4-turbo-preview"  # أو gpt-3.5-turbo للسرعة
    TEMPERATURE = 0.3  # قيمة منخفضة للدقة
    MAX_TOKENS = 2048


class OpenAIConnector:
    """التواصل مع OpenAI API"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = OpenAIConfig.BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_code(self, prompt):
        """توليد كود Blender من أمر طبيعي"""
        try:
            system_message = """أنت مساعد ذكي متخصص في كود Blender Python.
            عندما يطلب المستخدم إنشاء شيء ما، اكتب كود Python نظيف وآمن لـ Blender.
            الكود يجب أن يكون:
            1. آمن وخالي من الأخطاء
            2. مختصر وفعّال
            3. يستخدم Blender Python API
            4. يشرح نفسه بالتعليقات
            
            أمثلة:
            - "Create a red cube" => بنية كود إنشاء مكعب أحمر
            - "Add lighting" => بنية كود إضافة إضاءة احترافية
            - "Position camera" => بنية كود تموضع الكاميرا
            """
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": OpenAIConfig.MODEL,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": OpenAIConfig.TEMPERATURE,
                    "max_tokens": OpenAIConfig.MAX_TOKENS
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return self.extract_code(content)
            else:
                return None
                
        except Exception as e:
            print(f"❌ خطأ في الاتصال: {str(e)}")
            return None
    
    def extract_code(self, text):
        """استخراج كود Python من النص"""
        # البحث عن كود Python داخل markdown
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()


class BlenderSceneManager:
    """إدارة مشهد Blender"""
    
    @staticmethod
    def clear_scene():
        """حذف جميع الكائنات"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
    
    @staticmethod
    def add_cube(location=(0, 0, 0), scale=(1, 1, 1), color=(1, 0, 0, 1)):
        """إضافة مكعب"""
        bpy.ops.mesh.primitive_cube_add(location=location)
        obj = bpy.context.active_object
        obj.scale = scale
        BlenderSceneManager.set_color(obj, color)
        return obj
    
    @staticmethod
    def add_sphere(location=(0, 0, 0), radius=1, color=(0, 0, 1, 1)):
        """إضافة كرة"""
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
        obj = bpy.context.active_object
        BlenderSceneManager.set_color(obj, color)
        return obj
    
    @staticmethod
    def add_plane(location=(0, 0, 0), scale=(1, 1, 1)):
        """إضافة سطح مستوي"""
        bpy.ops.mesh.primitive_plane_add(location=location)
        obj = bpy.context.active_object
        obj.scale = scale
        return obj
    
    @staticmethod
    def add_light(location=(5, 5, 10), light_type='SUN'):
        """إضافة إضاءة"""
        bpy.ops.object.light_add(type=light_type, location=location)
        return bpy.context.active_object
    
    @staticmethod
    def add_camera(location=(7, -7, 5)):
        """إضافة كاميرا"""
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.active_object
        bpy.context.scene.camera = camera
        return camera
    
    @staticmethod
    def set_color(obj, color):
        """تعيين لون للكائن"""
        mat = bpy.data.materials.new(name="Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = color
        obj.data.materials.append(mat)
    
    @staticmethod
    def get_scene_info():
        """الحصول على معلومات المشهد"""
        objects = len(bpy.context.scene.objects)
        meshes = len([o for o in bpy.context.scene.objects if o.type == 'MESH'])
        lights = len([o for o in bpy.context.scene.objects if o.type == 'LIGHT'])
        return {
            "total_objects": objects,
            "meshes": meshes,
            "lights": lights
        }


class BlenderAIAssistant:
    """المساعد الذكي للـ Blender"""
    
    def __init__(self, api_key):
        self.connector = OpenAIConnector(api_key)
        self.command_history = []
    
    def execute_ai_command(self, user_input):
        """تنفيذ أمر من المستخدم"""
        print(f"\n🎨 الأمر: {user_input}")
        
        # توليد الكود
        code = self.connector.generate_code(user_input)
        if not code:
            print("❌ فشل توليد الكود")
            return False
        
        print(f"\n📝 الكود المولد:\n{code}\n")
        
        # تنفيذ الكود
        try:
            exec(code, {"bpy": bpy, "BlenderSceneManager": BlenderSceneManager})
            print("✅ تم التنفيذ بنجاح!")
            self.command_history.append({
                "timestamp": datetime.now().isoformat(),
                "command": user_input,
                "code": code,
                "status": "success"
            })
            return True
        except Exception as e:
            print(f"❌ خطأ في التنفيذ: {str(e)}")
            return False
    
    def interactive_mode(self):
        """الوضع التفاعلي"""
        print("\n" + "="*50)
        print("🤖 مساعد Blender الذكي - الوضع التفاعلي")
        print("="*50)
        print("اكتب أوامرك (اكتب 'exit' للخروج)\n")
        
        while True:
            try:
                command = input("🎯 > ").strip()
                if command.lower() == 'exit':
                    break
                if command.lower() == 'info':
                    info = BlenderSceneManager.get_scene_info()
                    print(f"📊 معلومات المشهد: {info}")
                    continue
                
                self.execute_ai_command(command)
            except KeyboardInterrupt:
                print("\n👋 تم الخروج")
                break
    
    def get_history(self):
        """الحصول على سجل الأوامر"""
        return self.command_history


# Blender Addon Panel
class BLENDER_AI_PT_Panel(bpy.types.Panel):
    """لوحة AI في Blender"""
    bl_label = "AI Tools"
    bl_idname = "BLENDER_AI_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Assistant'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # العنوان
        layout.label(text="🤖 Blender AI Assistant")
        layout.separator()
        
        # إدخال API Key
        layout.label(text="API Configuration:")
        layout.prop(scene, "ai_api_key", text="API Key")
        
        # حقل الأمر
        layout.label(text="Command:")
        layout.prop(scene, "ai_command", text="")
        
        # الأزرار
        layout.separator()
        col = layout.column()
        col.scale_y = 1.5
        col.operator("wm.ai_execute", text="Execute Command", icon="PLAY")
        col.operator("wm.ai_clear_scene", text="Clear Scene", icon="TRASH")
        
        # المعلومات
        layout.separator()
        layout.label(text="Scene Info:")
        info = BlenderSceneManager.get_scene_info()
        layout.label(text=f"Objects: {info['total_objects']}")
        layout.label(text=f"Meshes: {info['meshes']}")
        layout.label(text=f"Lights: {info['lights']}")


class WM_OT_AIExecute(bpy.types.Operator):
    """تنفيذ أمر AI"""
    bl_idname = "wm.ai_execute"
    bl_label = "Execute"
    
    def execute(self, context):
        scene = context.scene
        api_key = scene.ai_api_key
        command = scene.ai_command
        
        if not api_key:
            self.report({'ERROR'}, "❌ أدخل API Key أولاً")
            return {'CANCELLED'}
        
        if not command:
            self.report({'ERROR'}, "❌ أدخل أمراً")
            return {'CANCELLED'}
        
        assistant = BlenderAIAssistant(api_key)
        if assistant.execute_ai_command(command):
            self.report({'INFO'}, "✅ تم التنفيذ بنجاح")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "❌ فشل التنفيذ")
            return {'CANCELLED'}


class WM_OT_AIClearScene(bpy.types.Operator):
    """مسح المشهد"""
    bl_idname = "wm.ai_clear_scene"
    bl_label = "Clear"
    
    def execute(self, context):
        BlenderSceneManager.clear_scene()
        return {'FINISHED'}


def register_properties():
    """تسجيل الخصائص"""
    bpy.types.Scene.ai_api_key = bpy.props.StringProperty(
        name="API Key",
        description="OpenAI API Key",
        default=""
    )
    bpy.types.Scene.ai_command = bpy.props.StringProperty(
        name="Command",
        description="Blender AI Command",
        default=""
    )


def register():
    """تسجيل الـ Addon"""
    bpy.utils.register_class(BLENDER_AI_PT_Panel)
    bpy.utils.register_class(WM_OT_AIExecute)
    bpy.utils.register_class(WM_OT_AIClearScene)
    register_properties()
    print("✅ Blender AI Addon تم تثبيته بنجاح")


def unregister():
    """إلغاء تسجيل الـ Addon"""
    bpy.utils.unregister_class(BLENDER_AI_PT_Panel)
    bpy.utils.unregister_class(WM_OT_AIExecute)
    bpy.utils.unregister_class(WM_OT_AIClearScene)


if __name__ == "__main__":
    register()
    print("""
    ╔════════════════════════════════════════╗
    ║  🤖 Blender OpenAI Integration 🎨     ║
    ║                                        ║
    ║  مساعد ذكي لـ Blender يستخدم ChatGPT ║
    ║                                        ║
    ╚════════════════════════════════════════╝
    
    📖 الاستخدام:
    1. استبدل 'sk-your-api-key-here' بـ API Key الخاص بك
    2. في Blender: View > Sidebar > AI Assistant
    3. أدخل أوامرك بلغة طبيعية
    4. اضغط Execute
    
    أمثلة:
    - "Create a red cube"
    - "Add professional lighting"
    - "Position the camera"
    """)