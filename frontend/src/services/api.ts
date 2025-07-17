const API_BASE_URL = "http://localhost:8000";

export const apiService = {
  // Chat API
  async sendChatMessage(userMessage: string) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "accept": "application/json",
      },
      body: JSON.stringify({ user_message: userMessage }),
    });

    if (!response.ok) {
      throw new Error(`Chat API error: ${response.status}`);
    }

    return response.json();
  },

  // Upload API
  async uploadFile(file: File, title: string) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload API error: ${response.status}`);
    }

    return response.json();
  },
}; 