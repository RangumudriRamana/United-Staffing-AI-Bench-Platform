import api from "@/api/axios";
import type { Task } from "@/features/tasks/types";

class TaskService {
  async getMyTasks(): Promise<Task[]> {
    const response = await api.get("/tasks/my");
    return response.data;
  }

  async complete(publicId: string): Promise<Task> {
    const response = await api.post(
      `/tasks/${publicId}/complete`
    );

    return response.data;
  }
}

export default new TaskService();