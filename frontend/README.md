# Finance Assistant Chat Application

A modern, modular React application with AI-powered financial assistance capabilities.

## 🏗️ Project Structure

```
src/
├── components/
│   ├── layout/           # Layout components
│   │   ├── Header.tsx
│   │   └── Hero.tsx
│   ├── ui/              # Reusable UI components
│   ├── CardAnimated.tsx # Animated card components
│   ├── ChatComponent.tsx # Main chat interface
│   ├── Footer.tsx       # Footer component
│   ├── Background.tsx   # Shader gradient background
│   └── home.tsx         # Main landing page
├── data/                # Static data and configurations
│   └── cards.ts
├── hooks/               # Custom React hooks
│   └── useChat.ts
├── services/            # API and external services
│   └── api.ts
├── types/               # TypeScript type definitions
│   └── index.ts
├── utils/               # Utility functions
│   └── fileUtils.ts
└── main.tsx            # Application entry point
```

## 🚀 Features

### Core Functionality
- **AI Chat Interface**: Real-time conversation with AI assistant
- **File Upload**: PDF document upload with progress tracking
- **Animated Cards**: Interactive feature cards with smooth animations
- **Responsive Design**: Mobile-first responsive layout
- **Shader Background**: Advanced 3D gradient background effects

### Technical Features
- **Modular Architecture**: Clean separation of concerns
- **Type Safety**: Full TypeScript implementation
- **Custom Hooks**: Reusable state management
- **API Service Layer**: Centralized API communication
- **Utility Functions**: Reusable helper functions

## 🛠️ Architecture

### Components
- **Layout Components**: Header, Hero, Footer for page structure
- **UI Components**: Reusable design system components
- **Feature Components**: Chat, Cards, Background effects

### State Management
- **Custom Hooks**: `useChat` for chat functionality
- **Local State**: Component-level state management
- **API Integration**: Centralized service layer

### Data Flow
1. **User Interaction** → Component
2. **Component** → Custom Hook
3. **Custom Hook** → API Service
4. **API Service** → Backend
5. **Response** → UI Update

## 📦 Key Modules

### `useChat` Hook
Manages chat state and API communication:
```typescript
const { messages, sendMessage } = useChat();
```

### `apiService`
Centralized API communication:
```typescript
await apiService.sendChatMessage(message);
await apiService.uploadFile(file, title);
```

### `fileUtils`
File handling utilities:
```typescript
const sanitizedName = fileUtils.sanitizeFileName(file.name);
```

### `CardAnimated`
Interactive animated cards with Framer Motion:
```typescript
<CardsGrid cards={cardsData} />
```

### `Background`
Advanced 3D shader gradient background:
```typescript
<Background />
```

## 🎨 Styling

### CSS Architecture
- **Tailwind CSS**: Utility-first styling
- **Shader Gradients**: Advanced 3D background effects
- **Responsive Design**: Mobile-first approach

### Background Effects
- **Shader Gradients**: 3D animated gradient spheres
- **Real-time Animation**: Smooth color transitions
- **Performance Optimized**: Hardware-accelerated rendering

## 🔧 Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
```bash
npm install
```

### Development Server
```bash
npm run dev
```

### Build
```bash
npm run build
```

## 📱 Responsive Design

The application is fully responsive with:
- **Mobile-first approach**
- **Flexible grid layouts**
- **Adaptive typography**
- **Touch-friendly interactions**

## 🔄 State Management

### Chat State
- Message history
- Loading states
- File upload progress
- Error handling

### UI State
- Chat open/close
- Animation states
- Form validation

## 🎯 Future Enhancements

- [ ] User authentication
- [ ] Message persistence
- [ ] Advanced file processing
- [ ] Real-time notifications
- [ ] Analytics integration
- [ ] Performance optimizations

## 📄 License

MIT License - see LICENSE file for details.
