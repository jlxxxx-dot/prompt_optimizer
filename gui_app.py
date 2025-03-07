import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from backend.core.optimizer import PromptOptimizer
import time

class PromptOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Prompt Optimizer 🚀')
        self.root.geometry('1200x800')

        # 初始化优化器
        self.optimizer = PromptOptimizer()

        # 获取可用模型列表
        self.available_models = self.get_available_models()

        # 主题设置
        self.dark_mode = False
        self.setup_theme()

        # 历史记录
        self.history = []

        # 创建界面组件
        self.create_widgets()

    def setup_theme(self):
        # 配置主题颜色
        self.light_theme = {
            'bg': '#ffffff',
            'fg': '#000000',
            'button_bg': '#f0f0f0',
            'text_bg': '#ffffff',
            'text_fg': '#000000'
        }
        self.dark_theme = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'button_bg': '#3b3b3b',
            'text_bg': '#1e1e1e',
            'text_fg': '#ffffff'
        }
        self.current_theme = self.light_theme

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.current_theme = self.dark_theme if self.dark_mode else self.light_theme
        self.apply_theme()

    def apply_theme(self):
        self.root.configure(bg=self.current_theme['bg'])
        for widget in [self.input_text, self.result_text]:
            widget.configure(
                bg=self.current_theme['text_bg'],
                fg=self.current_theme['text_fg'],
                insertbackground=self.current_theme['text_fg']
            )
        for button in [self.theme_btn, self.prompt_btn, self.history_btn,
                      self.model_btn, self.test_btn]:
            button.configure(
                bg=self.current_theme['button_bg'],
                fg=self.current_theme['fg']
            )

    def create_widgets(self):
        # 顶部按钮栏
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=10, pady=5)

        self.theme_btn = tk.Button(
            button_frame,
            text='🌙 日间模式' if self.dark_mode else '☀️ 夜间模式',
            command=self.toggle_theme
        )
        self.prompt_btn = tk.Button(button_frame, text='📝 功能提示词', command=self.show_templates)
        self.history_btn = tk.Button(button_frame, text='📜 历史记录', command=self.show_history)
        self.model_btn = tk.Button(button_frame, text='⚙️ 模型管理', command=self.show_model_management)

        for i, btn in enumerate([self.theme_btn, self.prompt_btn,
                                self.history_btn, self.model_btn]):
            btn.pack(side='left', padx=5)

        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=5)

        # 主要内容区域
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # 输入区域
        ttk.Label(content_frame, text='提示词').pack(anchor='w')
        self.input_text = scrolledtext.ScrolledText(
            content_frame, height=10, width=80
        )
        self.input_text.pack(fill='both', expand=True, pady=5)

        # 模型选择和测试按钮区域
        model_frame = ttk.Frame(content_frame)
        model_frame.pack(fill='x', pady=5)

        # 模型选择（居左）
        model_label_frame = ttk.Frame(model_frame)
        model_label_frame.pack(side='left', fill='x', expand=True)

        ttk.Label(model_label_frame, text='模型').pack(side='left')
        self.model_var = tk.StringVar(value=self.available_models[0] if self.available_models else '无可用模型')
        self.model_select = ttk.Combobox(
            model_label_frame,
            textvariable=self.model_var,
            values=self.available_models,
            state='readonly',
            width=30
        )
        self.model_select.pack(side='left', padx=(10, 0))

        # 测试按钮（居右）
        self.test_btn = tk.Button(
            model_frame,
            text='提示词优化 →',
            command=self.run_test
        )
        self.test_btn.pack(side='right')
        self.test_btn.pack(pady=10)

        # 结果区域（使用Frame包装两个结果窗口）
        results_frame = ttk.Frame(content_frame)
        results_frame.pack(fill='both', expand=True, pady=10)

        # 分析结果区域（左侧）
        analysis_frame = ttk.Frame(results_frame)
        analysis_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        ttk.Label(analysis_frame, text='提示词分析结果').pack(anchor='w')
        self.result_text = scrolledtext.ScrolledText(
            analysis_frame, height=15, width=40, state='disabled'
        )
        self.result_text.pack(fill='both', expand=True)

        # 优化结果区域（右侧）
        optimization_frame = ttk.Frame(results_frame)
        optimization_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        ttk.Label(optimization_frame, text='优化后的提示词').pack(anchor='w')
        self.optimized_text = scrolledtext.ScrolledText(
            optimization_frame, height=15, width=40, state='disabled'
        )
        self.optimized_text.pack(fill='both', expand=True)

        # 应用主题
        self.apply_theme()

    def get_available_models(self):
        try:
            # 使用ollama adapter获取可用模型列表
            models = self.optimizer.ollama.list_models()
            return models if models else ['无可用模型']
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return ['无可用模型']

    def run_test(self):
        user_input = self.input_text.get('1.0', 'end-1c')
        model = self.model_var.get()

        if not user_input or model == '无可用模型':
            tk.messagebox.showwarning('警告', '请输入测试内容并选择模型')
            return

        # 启用结果文本框并清空
        self.result_text.configure(state='normal')
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('1.0', '正在分析提示词...')
        self.result_text.configure(state='disabled')

        # 清空优化结果文本框
        self.optimized_text.configure(state='normal')
        self.optimized_text.delete('1.0', 'end')
        self.optimized_text.insert('1.0', '正在优化提示词...')
        self.optimized_text.configure(state='disabled')
        self.root.update()

        # 分析提示词
        analysis = self.optimizer.analyze_prompt(user_input)

        # 分步显示分析结果
        self.result_text.configure(state='normal')
        self.result_text.delete('1.0', 'end')
        
        # 显示基础分析结果
        base_result = f"分析结果：\n"
        self.result_text.insert('end', base_result)
        self.root.update()
        
        # 显示评分
        scores = f"结构完整性：{analysis.structure_score}\n"
        self.result_text.insert('end', scores)
        self.root.update()
        
        scores = f"表达清晰度：{analysis.clarity_score}\n"
        self.result_text.insert('end', scores)
        self.root.update()
        
        scores = f"内容完整性：{analysis.completeness_score}\n\n"
        self.result_text.insert('end', scores)
        self.root.update()

        # 显示优化建议
        if analysis.suggestions:
            self.result_text.insert('end', '优化建议：\n')
            for suggestion in analysis.suggestions:
                self.result_text.insert('end', f'- {suggestion}\n')
        self.result_text.configure(state='disabled')

        # 优化提示词并显示结果
        try:
            optimized_prompt = self.optimizer.optimize_prompt(user_input)
            self.optimized_text.configure(state='normal')
            self.optimized_text.delete('1.0', 'end')
            self.optimized_text.insert('1.0', optimized_prompt)
            self.optimized_text.configure(state='disabled')
        except Exception as e:
            self.optimized_text.configure(state='normal')
            self.optimized_text.delete('1.0', 'end')
            self.optimized_text.insert('1.0', f'优化失败：{str(e)}')
            self.optimized_text.configure(state='disabled')

        # 显示优点
        if analysis.strengths:
            self.result_text.insert('end', "\n优点：\n")
            for i, strength in enumerate(analysis.strengths, 1):
                self.result_text.insert('end', f"{i}. {strength}\n")
                self.root.update()
                time.sleep(0.1)

        # 显示不足
        if analysis.weaknesses:
            self.result_text.insert('end', "\n不足：\n")
            for i, weakness in enumerate(analysis.weaknesses, 1):
                self.result_text.insert('end', f"{i}. {weakness}\n")
                self.root.update()
                time.sleep(0.1)

        self.result_text.configure(state='disabled')

        # 添加到历史记录
        self.history.append({
            'prompt': user_input,
            'result': self.result_text.get('1.0', 'end-1c'),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })

    def show_templates(self):
        template_window = tk.Toplevel(self.root)
        template_window.title('功能提示词模板')
        template_window.geometry('600x400')

        for name, template in self.optimizer.templates.items():
            frame = ttk.Frame(template_window)
            frame.pack(fill='x', padx=10, pady=5)

            ttk.Label(frame, text=name.capitalize()).pack(side='left')
            apply_btn = ttk.Button(
                frame,
                text='应用',
                command=lambda t=template: self.apply_template(t)
            )
            apply_btn.pack(side='right')

            text = scrolledtext.ScrolledText(template_window, height=5)
            text.insert('1.0', template)
            text.configure(state='disabled')
            text.pack(fill='x', padx=10, pady=5)

    def apply_template(self, template):
        self.input_text.delete('1.0', 'end')
        self.input_text.insert('1.0', template)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title('历史记录')
        history_window.geometry('800x600')

        for entry in reversed(self.history):
            frame = ttk.Frame(history_window)
            frame.pack(fill='x', padx=10, pady=5)

            ttk.Label(frame, text=entry['timestamp']).pack(anchor='w')

            prompt_text = scrolledtext.ScrolledText(frame, height=3)
            prompt_text.insert('1.0', entry['prompt'])
            prompt_text.configure(state='disabled')
            prompt_text.pack(fill='x')

            result_text = scrolledtext.ScrolledText(frame, height=6)
            result_text.insert('1.0', entry['result'])
            result_text.configure(state='disabled')
            result_text.pack(fill='x')

            ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=5)

    def show_model_management(self):
        model_window = tk.Toplevel(self.root)
        model_window.title('模型管理')
        model_window.geometry('400x300')

        # 这里可以添加模型配置的界面
        # 例如：模型选择、参数配置等
        ttk.Label(model_window, text='模型配置（开发中）').pack(pady=20)

def main():
    root = tk.Tk()
    app = PromptOptimizerGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()