import requests
import logging
import json
import re

logger = logging.getLogger("notifier")

class Notifier:
    def __init__(self, feishu_webhook=None, dingtalk_webhook=None):
        self.feishu_webhook = feishu_webhook
        self.dingtalk_webhook = dingtalk_webhook

    def send(self, title, content):
        """
        发送通知到所有配置的渠道
        """
        if self.feishu_webhook:
            self._send_feishu(title, content)
        
        if self.dingtalk_webhook:
            self._send_dingtalk(title, content)

    def _optimize_feishu_content(self, content):
        """
        优化 Markdown 内容以适配飞书卡片展示
        主要处理：
        1. 将 Markdown 表格转换为列表形式，避免手机端乱码
        2. 增加视觉分割
        """
        lines = content.split('\n')
        optimized_lines = []
        in_table = False
        table_headers = []
        
        for line in lines:
            line = line.strip()
            
            # 检测表格分隔行 |---|---| 或 |:---|:---|
            # 只要包含三个以上的 |- 或 |: ，就认为是分隔行
            # 正则解释：
            # ^\| : 以 | 开头
            # .*[-:]{3,}.* : 中间包含至少3个连续的 - 或 :
            # \|$ : 以 | 结尾
            if re.match(r'^\|.*[-:]{3,}.*\|$', line):
                in_table = True
                continue
                
            # 检测表格数据行 | A | B |
            # 只要以 | 开头并以 | 结尾，就尝试解析
            if line.startswith('|') and line.endswith('|'):
                # 提取单元格数据
                cells = [c.strip() for c in line.strip('|').split('|')]
                
                # 如果当前不在表格模式，但遇到了看起来像表格行的数据
                # 我们假设这是表头，直接开启表格模式并跳过显示
                # (因为列表视图不需要表头)
                if not in_table:
                    in_table = True
                    table_headers = cells
                    continue
                
                # 数据行处理
                
                # 数据行处理
                if len(cells) >= 3:
                    # 假设格式：币种 | 赛道 | 涨跌幅 | 评价
                    # 转换为：**币种** (赛道) 涨跌幅
                    #        > 评价
                    
                    # 尝试智能识别列
                    coin = cells[0]
                    # 简单的格式化
                    formatted_item = f"🔹 **{coin}**"
                    if len(cells) > 1:
                        formatted_item += f"  |  {cells[1]}"
                    if len(cells) > 2:
                        formatted_item += f"  |  {cells[2]}"
                    
                    optimized_lines.append(formatted_item)
                    
                    if len(cells) > 3:
                        # 评价部分换行显示，并用引用样式
                        # 检查评价部分是否为空或仅包含空白字符
                        comment = cells[3].strip()
                        if comment:
                             optimized_lines.append(f"    └  {comment}")
                    
                    optimized_lines.append("") # 空行分隔
                else:
                    # 兜底：列数不够，直接显示原样（去掉首尾|）
                    optimized_lines.append(f"• {line.strip('|')}")
            else:
                # 非表格行
                if in_table and line == "":
                    in_table = False # 表格结束
                
                # 优化标题：飞书 lark_md 支持 **加粗**，但对 ### 支持一般
                # 手动给标题加个 Emoji 或分割线效果
                if line.startswith('### ') or line.startswith('## ') or line.startswith('**'):
                    if optimized_lines and optimized_lines[-1] != "":
                        optimized_lines.append("--------------------------------------------------")
                    optimized_lines.append(line)
                else:
                    optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def _send_feishu(self, title, content):
        """
        发送飞书消息
        """
        headers = {'Content-Type': 'application/json'}
        
        # 1. 优化内容格式
        optimized_content = self._optimize_feishu_content(content)
        
        # 2. 构造卡片
        # 为了更好的视觉效果，我们可以根据内容长度或特定标记拆分 elements
        # 但简单起见，我们先用一个优化后的 lark_md 块
        
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": title
                    },
                    "template": "blue" # 标题栏颜色
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": optimized_content
                        }
                    },
                    {
                        "tag": "hr" # 底部加一条分割线
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {
                                "tag": "plain_text",
                                "content": "Generated by OKX Research Analyst AI 🤖"
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            response = requests.post(self.feishu_webhook, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Feishu notification sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send Feishu notification: {e}")

    def _send_dingtalk(self, title, content):
        """
        发送钉钉消息
        """
        headers = {'Content-Type': 'application/json'}
        
        # 1. 优化内容格式
        # 虽然钉钉支持 Markdown 表格，但在移动端体验依然一般
        # 我们复用飞书的优化逻辑（转为列表），或者针对钉钉做微调
        # 这里为了保持体验一致性，且考虑到列表式阅读更友好，直接复用优化逻辑
        # 但钉钉 Markdown 语法与飞书略有不同（飞书是 lark_md），需要做一点适配
        
        # 获取通用优化后的文本 (基于飞书逻辑，主要是去表格化)
        base_optimized_content = self._optimize_feishu_content(content)
        
        # 钉钉 Markdown 适配：
        # 1. 飞书的 <lark_md> 标签在普通文本里没有，但 _optimize_feishu_content 返回的是纯文本（带格式）
        # 2. 钉钉支持标准 Markdown，所以 **加粗** 是通用的
        # 3. 钉钉引用是用 > ，飞书逻辑里用了 └ ，我们可以替换一下让它在钉钉更像引用
        
        ding_content = base_optimized_content.replace("    └", ">")
        
        # 增加底部签名
        ding_content += "\n\n---\n###### Generated by OKX Research Analyst AI 🤖"

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"# {title}\n\n{ding_content}"
            }
        }
        
        try:
            response = requests.post(self.dingtalk_webhook, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("DingTalk notification sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send DingTalk notification: {e}")
