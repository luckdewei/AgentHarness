# 导入 agent_loop 函数从 agent 模块
from agent import agent_loop


# 定义主函数
def main():
    # 打印提示信息，告诉用户如何退出
    print("输入问题，回车发送。输入 q 退出。\n")
    # 初始化历史消息列表
    history = []
    # 进入无限循环，不断接收用户输入
    while True:
        try:
            # 获取用户输入，带有提示符
            query = input("\x1b[36m>> \x1b[0m")
        # 捕获 EOFError 或 KeyboardInterrupt 异常（例如 Ctrl+D 或 Ctrl+C）
        except (EOFError, KeyboardInterrupt):
            # 异常时退出循环
            break
        # 如果输入为空，或者用户输入了 'q' 或 'exit'，则退出循环
        if query.strip().lower() in ("q", "exit", ""):
            break
        # 将用户输入添加到历史消息列表
        history.append({"role": "user", "content": query})
        # 调用代理循环处理用户和历史消息
        agent_loop(history)
        # 获取历史列表最后一条消息
        final = history[-1]
        # 如果最后一条消息是助手回复且有内容则输出该内容
        if final.get("role") == "assistant" and final.get("content"):
            print(final["content"])


# 如果当前脚本作为主程序运行，则调用 main 函数
if __name__ == "__main__":
    main()
