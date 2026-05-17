/**
 * Questions feature types.
 */

/**
 * 每日问答
 */
export interface DailyQuestion {
  id: number;
  date: string;
  content: string;
  answerA?: string;
  answerB?: string;
}

/**
 * 题库项
 */
export interface QuestionBankItem {
  id: number;
  content: string;
  targetDate?: string;
  createdAt: string;
}

/**
 * 默认问答问题
 */
export const DEFAULT_QUESTIONS = [
  "如果中彩票了第一件事做什么？",
  "你最喜欢我哪一点？",
  "如果可以穿越时空，你想去哪里？",
  "我们第一次见面的场景你还记得吗？",
  "你觉得我们最默契的一件事是什么？",
  "最近一次让你感动的事情是什么？",
  "如果我们要一起养一只宠物，你会选什么？",
  "你觉得完美的周末应该怎么过？",
  "如果世界末日来了，你想吃什么？",
  "你最想和我一起完成的愿望是什么？",
];