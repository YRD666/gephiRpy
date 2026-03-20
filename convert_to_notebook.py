"""Convert tutorial_python.py to Jupyter Notebook with markdown cells for section headers."""

import json
import re

def py_to_notebook(py_path, nb_path):
    with open(py_path, "r", encoding="utf-8") as f:
        source = f.read()

    cells = []

    # Title cell
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# gephi-cli Python 完整使用教程\n",
            "\n",
            "本教程演示 gephi-cli 的所有功能模块：\n",
            "\n",
            "| 模块 | 功能 |\n",
            "|------|------|\n",
            "| 1. 图生成 | 11种图生成器 (随机、无标度、小世界等) |\n",
            "| 2. 图导入 | 边列表、邻接矩阵、字符串、pandas、NetworkX、文件 |\n",
            "| 3. 图导出 | GEXF/GraphML/CSV/GML、NetworkX、pandas |\n",
            "| 4. 图信息与验证 | 基本信息、结构质量报告 |\n",
            "| 5. 布局算法 | 11种布局 + 归一化 + 自动布局 |\n",
            "| 6. 图指标 | 15种指标 (度、PageRank、模块度等) |\n",
            "| 7. 过滤器 | 17种过滤器 |\n",
            "| 8. 外观样式 | 节点/边颜色、大小、标签 |\n",
            "| 9. 预览与导出 | PNG/PDF/SVG + 预设 |\n",
            "| 10. 数据实验室 | 节点/边CRUD、列操作 |\n",
            "| 11. 最短路径 | Dijkstra 算法 |\n",
            "| 12. 项目管理 | 工作区管理 |\n",
            "| 13. YAML 流水线 | 多步自动化 |\n",
            "\n",
            "**运行前请确保：**\n",
            "```bash\n",
            "pip install gephi-cli[all]\n",
            "python download_toolkit.py\n",
            "```"
        ]
    })

    # Remove the docstring
    source = re.sub(r'^"""[\s\S]*?"""\n*', '', source)

    # Split by section headers
    sections = re.split(r'(# =+\n# \d+\..*\n# =+\n)', source)

    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue

        # Check if this is a header
        header_match = re.match(r'# =+\n# (\d+\..+)\n# =+', section)
        if header_match:
            title = header_match.group(1).strip()
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"## {title}"]
            })
            continue

        # Code section - split into smaller cells at blank lines between logical blocks
        # but keep related lines together
        lines = section.split('\n')

        current_cell = []
        for line in lines:
            # Start new cell on print headers or section comments
            if (line.startswith('print("\\n"') or
                line.startswith('print("="') or
                (line.startswith('# ') and line.startswith('# ') and
                 re.match(r'^# \d+\.\d+ ', line))):
                if current_cell:
                    code = '\n'.join(current_cell).strip()
                    if code:
                        cells.append({
                            "cell_type": "code",
                            "metadata": {},
                            "source": [code],
                            "execution_count": None,
                            "outputs": []
                        })
                    current_cell = []

                # Convert numbered comments to markdown
                m = re.match(r'^# (\d+\.\d+ .+)$', line)
                if m:
                    cells.append({
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [f"### {m.group(1)}"]
                    })
                    continue

            current_cell.append(line)

        # Flush remaining
        if current_cell:
            code = '\n'.join(current_cell).strip()
            if code:
                cells.append({
                    "cell_type": "code",
                    "metadata": {},
                    "source": [code],
                    "execution_count": None,
                    "outputs": []
                })

    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.12.0"
            }
        },
        "cells": cells
    }

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)

    print(f"Created {nb_path} with {len(cells)} cells")

if __name__ == "__main__":
    py_to_notebook("tutorials/tutorial_python.py", "tutorials/tutorial_python.ipynb")
