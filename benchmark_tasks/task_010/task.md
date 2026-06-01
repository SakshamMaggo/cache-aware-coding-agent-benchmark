Fix the attempt summarizer.

It receives repair traces where each task has a list of attempts. It should count total tasks, count all attempts across tasks, and count a task as fixed if any of its attempts passed. It should also handle tasks with no attempts.