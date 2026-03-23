import os
import shutil
from pdf2image import convert_from_path
import time
import pyperclip  # 引入剪切板库

# --- 1. 用户配置 ---
# 输出文件名和文件夹
OUTPUT_IMAGE_FOLDER = "pic"

# --- 2. 功能函数 ---

def find_input_files():
    """在当前目录中自动查找一个PDF和一个TXT文件。"""
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    txt_files = [f for f in os.listdir('.') if f.lower().endswith('.txt')]

    # 验证PDF文件
    if len(pdf_files) == 0:
        print("错误：在当前目录中找不到 .pdf 文件。")
        return None, None
    elif len(pdf_files) > 1:
        print("错误：在当前目录中找到了多个 .pdf 文件，请只保留一个。")
        print("找到的文件:", pdf_files)
        return None, None

    # 验证TXT文件
    if len(txt_files) == 0:
        print("错误：在当前目录中找不到 .txt 字幕文件。")
        return None, None
    elif len(txt_files) > 1:
        print("错误：在当前目录中找到了多个 .txt 文件，请只保留一个。")
        print("找到的文件:", txt_files)
        return None, None
    
    pdf_filename = pdf_files[0]
    txt_filename = txt_files[0]
    
    print(f"--- 成功找到输入文件 ---")
    print(f"PDF文件: {pdf_filename}")
    print(f"字幕文件: {txt_filename}")
    
    return pdf_filename, txt_filename

def convert_pdf_to_png(pdf_path, output_folder):
    """
    检查文件夹是否存在。
    如果存在 -> 跳过转换。
    如果不存在 -> 创建文件夹并将PDF转换为PNG。
    """
    print(f"\n--- 步骤 1: 检查图片资源 ---")
    
    # 核心修改：检测文件夹是否存在
    if os.path.exists(output_folder):
        print(f"检测到文件夹 '{output_folder}' 已存在。")
        print(">>> 跳过 PDF 转图片步骤 (默认使用现有图片)。")
        return True
    
    # 如果代码运行到这里，说明文件夹不存在，需要进行转换
    print(f"文件夹 '{output_folder}' 不存在，开始创建并转换 PDF...")
    os.makedirs(output_folder)

    try:
        print(f"正在转换 {pdf_path} (这可能需要几十秒)...")
        images = convert_from_path(pdf_path, dpi=200)
        for i, image in enumerate(images):
            fname = f"page_{i + 1}.png"
            output_path = os.path.join(output_folder, fname)
            image.save(output_path, "PNG")
        print(f"成功将 {len(images)} 页转换为 PNG 并保存在 '{output_folder}' 文件夹中。")
        return True
    except Exception as e:
        print(f"错误：PDF 转换失败。")
        print(f"详细信息: {e}")
        print("请确保您已正确安装 Poppler 并将其添加到了系统路径中。")
        # 如果转换失败，删除可能创建了一半的空文件夹，以免下次误判
        if os.path.exists(output_folder) and not os.listdir(output_folder):
             os.rmdir(output_folder)
        return False

def generate_prompt_and_copy(pdf_file_path, text_file_path):
    """读取字幕文件，构建Prompt，并复制到剪切板"""
    print(f"\n--- 步骤 2: 构建 Prompt 并复制到剪切板 ---")
    
    try:
        # 1. 读取字幕文件内容
        print(f"正在读取字幕文件内容: {text_file_path}")
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                subtitles_content = f.read()
        except Exception as e:
            print(f"错误: 无法读取字幕文件。详细信息: {e}")
            return
            
        print("正在构建 Prompt...")

        # 3. 构建 Prompt
        final_prompt = f"""
你是一位顶尖的AI助教，专精于计算机科学与数学领域。你的核心任务是根据我提供的课程讲义PDF和对应的课程字幕文字，生成一份专业、详尽、教学价值高的LaTeX课程笔记。

请严格遵循以下规则，生成一份完整的、可以直接编译的`.tex`文件。

### 第一部分：LaTeX 文档结构与格式要求

1.  **完整文档**: 输出必须是一个从 `\\documentclass` 开始到 `\\end{{document}}` 结束的完整LaTeX代码。
2.  **文档模板**: 必须使用以下模板结构。请在 `%% --- 正文内容开始 --- %%` 和 `%% --- 正文内容结束 --- %%` 之间填充笔记核心内容。

    ```latex
    \\documentclass[a4paper]{{article}}

    % --- 基础宏包 ---
    \\usepackage{{ctex}}
    \\usepackage{{amsmath, amssymb}}
    \\usepackage{{graphicx}}
    \\usepackage[margin=2.5cm]{{geometry}}
    \\usepackage[most]{{tcolorbox}}
    \\usepackage{{listings}}
    \\usepackage{{hyperref}}

    % --- 自定义高亮盒子 ---
    % 蓝色补充知识框
    \\newtcolorbox{{knowledgebox}}[1]{{
        enhanced, colback=blue!5!white, colframe=blue!75!black, colbacktitle=blue!75!black,
        coltitle=white, fonttitle=\\bfseries, title=#1, attach boxed title to top left={{yshift=-2mm, xshift=2mm}},
        boxrule=1pt, sharp corners
    }}
    % 黄色核心概念框
    \\newtcolorbox{{importantbox}}[1]{{
        enhanced, colback=yellow!10!white, colframe=yellow!80!black, colbacktitle=yellow!80!black,
        coltitle=black, fonttitle=\\bfseries, title=#1, sharp corners
    }}
    % 红色常见误区框
    \\newtcolorbox{{warningbox}}[1]{{
        enhanced, colback=red!5!white, colframe=red!75!black, colbacktitle=red!75!black,
        coltitle=white, fonttitle=\\bfseries, title=#1, sharp corners
    }}

    % --- 代码块样式定义 ---
    \\lstset{{
        language=Python,
        basicstyle=\\ttfamily\\small,
        keywordstyle=\\color{{blue}},
        stringstyle=\\color{{red!60!black}},
        commentstyle=\\color{{green!60!black}},
        breaklines=true,
        frame=single,
        numbers=left,
        numberstyle=\\tiny\\color{{gray}},
        captionpos=b,
        extendedchars=false
    }}

    % --- 文档标题信息 ---
    \\title{{课程笔记：[请根据PDF和字幕内容填写课程主题]}}
    \\author{{Gemini 2.5-pro \\& 田沛骐}}
    \\date{{\\today}}

    \\begin{{document}}

    \\maketitle
    \\tableofcontents
    \\newpage

    %% --- 正文内容开始 --- %%

    % 笔记正文将在此处生成...

    %% --- 正文内容结束 --- %%

    \\end{{document}}
    ```

### 第二部分：笔记内容生成规则

1.  **内容来源**: 综合利用PDF讲义的结构、标题、图表、公式和字幕中的口头解释、实例、强调重点来生成笔记。必须跳过所有与课程知识无关的闲聊、问候等logistic。
2.  **结构化**: 使用 `\\section{{...}}` 和 `\\subsection{{...}}` 来组织内容，确保逻辑清晰。
3.  **图片引用**: 当需要引用讲义中的幻灯片时，严格使用 `\\includegraphics[width=\\textwidth]{{pic/page_N.png}}` 命令，其中 `N` 是PDF的页码。并在图片下方使用 `\\caption{{}}` 命令添加合适的图注。
4.  **公式讲解**: 遇到数学公式时，先用 `$$...$$` 展示公式，然后必须紧跟一个列表，详细解释公式中每个符号的含义。
5.  **代码块**: 所有代码示例必须使用 `listings` 环境包裹，并添加 `caption` 来说明代码功能，例如：`\\begin{{lstlisting}}[language=Python, caption={{示例：使用梯度下降法寻找函数最小值}}] ... \\end{{lstlisting}}`。
6.  **教学高亮**:
    * **核心概念**: 对于课程中的关键定义或基石概念，使用 `\\begin{{importantbox}}{{核心概念：...}} ... \\end{{importantbox}}`。
    * **补充知识**: 对于背景知识、技术演进（如7nm/5nm的例子）、或趣闻轶事，使用 `\\begin{{knowledgebox}}{{补充知识：...}} ... \\end{{knowledgebox}}`。
    * **常见误区**: 对于学生容易犯错或理解有偏差的地方，使用 `\\begin{{warningbox}}{{常见误区：...}} ... \\end{{warningbox}}` 进行警示。
7.  **总结与拓展**: 在每个主要章节 (`\\section`) 的末尾，必须添加一个 `\\subsection{{本章小结}}` 进行总结，并酌情添加 `\\subsection{{拓展阅读}}` 提供1-2个高质量的外部链接。
8.  **语言**: 所有笔记内容使用中文。

9. **限制**:你不能在自定义的消息盒子中插入图片 !!!
10. **限制**:你不能在生成的latex代码中插入[cite]这样的引用。

        --- 课程字幕开始 ---
        {subtitles_content}
        --- 课程字幕结束 ---
请根据以上全部规则，开始生成课程笔记。
        """
        
        # 4. 复制到剪切板
        pyperclip.copy(final_prompt)
        
        print(f"\nSUCCESS! Prompt 已成功复制到系统剪切板。")
        print("-" * 50)
        print("【下一步操作指引】：")
        print("1. 打开 Gemini / ChatGPT 网页版。")
        print(f"2. 手动上传 PDF 文件: {pdf_file_path}")
        print("3. 在输入框中按 Ctrl+V (粘贴)。")
        print("-" * 50)

    except Exception as e:
        print(f"\n错误: 处理 Prompt 失败。详细信息: {e}")


# --- 4. 主执行流程 ---
if __name__ == "__main__":
    # 步骤 0: 查找输入文件
    pdf_filename, subtitles_filename = find_input_files()
    
    if pdf_filename and subtitles_filename:
        # 步骤 1: 图片处理 (如果文件夹已存在则跳过)
        if convert_pdf_to_png(pdf_filename, OUTPUT_IMAGE_FOLDER):
            # 步骤 2: 生成 Prompt 并复制
            generate_prompt_and_copy(pdf_filename, subtitles_filename)
