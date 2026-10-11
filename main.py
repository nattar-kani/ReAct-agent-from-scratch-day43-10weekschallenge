from src.agent import ReActAgent


def main():
    agent = ReActAgent()

    task = (
        "Calculate the total cost of 3 notebooks at 45 rupees each "
        "and 2 pens at 10 rupees each. Use the calculator tool."
    )

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


if __name__ == "__main__":
    main()
