/**
 * Questions feature API module.
 */
import { apiClient, unwrap } from "@/api/client";

export interface DailyQuestion {
  id: number;
  date: string;
  content: string;
  answerA?: string;
  answerB?: string;
}

export interface QuestionBankItem {
  id: number;
  content: string;
  targetDate?: string;
  createdAt: string;
}

export interface CreateQuestionRequest {
  content: string;
  targetDate?: string;
}

export interface AnswerRequest {
  answerA?: string;
  answerB?: string;
}

export const questionsApi = {
  getToday: () =>
    unwrap(apiClient.get<DailyQuestion>("/today")),

  answerQuestion: (id: number, data: AnswerRequest) =>
    unwrap(apiClient.post<DailyQuestion>(`/today/answer`, data)),

  getHistory: (limit = 30) =>
    unwrap(apiClient.get<DailyQuestion[]>("/history", { params: { limit } })),

  // Question bank
  getQuestionBank: () =>
    unwrap(apiClient.get<QuestionBankItem[]>("/bank")),

  createQuestion: (data: CreateQuestionRequest) =>
    unwrap(apiClient.post<QuestionBankItem>("/bank", data)),

  updateQuestion: (id: number, data: CreateQuestionRequest) =>
    unwrap(apiClient.put<QuestionBankItem>(`/bank/${id}`, data)),

  deleteQuestion: (id: number) =>
    unwrap(apiClient.delete(`/bank/${id}`)),
};