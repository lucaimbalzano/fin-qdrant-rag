# Frontend-Backend Integration Guide

## 1. API Contract

- **Send Message:**  
  - **Endpoint:** `POST /chat`
  - **Request Body:**
    ```json
    {
      "user_message": "string"
    }
    ```
  - **Response:**
    ```json
    {
      "bot_response": "string",
      "timestamp": "ISO8601 string",
      "metadata": {
        "message_id": "number"
        // ...other metadata
      }
    }
    ```

- **(Optional) Message History:**  
  - If you want to display previous messages, implement an endpoint like `GET /messages` or `/history`.

---

## 2. Frontend Data Model

- Each message should be an object:
  ```ts
  interface ChatMessage {
    id: string; // Use message_id from backend or generate for user messages
    content: string;
    sender: "user" | "assistant";
    timestamp: Date;
  }
  ```

---

## 3. Message Flow

- When the user sends a message:
  1. Add the user message to the local state immediately.
  2. Send a `POST` request to `/chat` with the message content.
  3. When the backend responds, add the assistant’s message to the state using the response data.

---

## 4. Component Responsibilities

- **ChatComponent.tsx**  
  - Renders the chat UI and message list.
  - Handles input and send actions.
  - Calls `onSendMessage` prop with the user’s message.

- **Parent Component**  
  - Manages the `messages` array.
  - Handles API calls to the backend.
  - Updates the message list with both user and assistant messages.

---

## 5. Backend Integration Example

```tsx
// Pseudocode for parent component
const [messages, setMessages] = useState<ChatMessage[]>([]);

async function handleSendMessage(userContent: string) {
  const userMsg: ChatMessage = {
    id: generateId(),
    content: userContent,
    sender: 'user',
    timestamp: new Date(),
  };
  setMessages(prev => [...prev, userMsg]);

  const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_message: userContent }),
  });
  const data = await response.json();

  const assistantMsg: ChatMessage = {
    id: data.metadata?.message_id?.toString() || generateId(),
    content: data.bot_response,
    sender: 'assistant',
    timestamp: new Date(data.timestamp),
  };
  setMessages(prev => [...prev, assistantMsg]);
}
```

---

## 6. Session & Persistence (Optional)

- If you want to persist chat history, implement user/session management on the backend and fetch history on component mount.

---

## 7. Error Handling

- Show a user-friendly error if the backend is unreachable or returns an error.
- Optionally, retry failed requests.

---

## 8. Styling & UX

- Continue using Tailwind CSS and animated avatars.
- Ensure the chat auto-scrolls to the latest message after each update.

---

## 9. Summary for the Team

- The frontend should treat the backend as the source of truth for assistant responses and (optionally) message history.
- All message state is managed in the parent component, which interfaces with the backend for sending and receiving messages.
- The backend is responsible for generating responses, storing messages, and (optionally) managing sessions.

---

**Next Steps:**  
- Refactor your parent component to handle API calls as described.
- Ensure your message model matches the backend contract.
- Test the integration by sending messages and verifying assistant responses are shown in the chat.
