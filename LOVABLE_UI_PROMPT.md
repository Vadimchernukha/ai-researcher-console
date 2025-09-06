# AI Researcher Console - UI/UX Specification for Lovable

## Project Overview
Create a modern, professional web application for AI-powered website analysis and classification. The app should have a clean, scientific aesthetic with excellent UX for researchers and analysts.

## Core Features & Pages

### 1. Authentication
- **Login Page**: Clean form with email/password
- **Sign Up Page**: Registration with email verification
- **Password Reset**: Forgot password flow
- **Session Management**: Auto-logout, session persistence

### 2. Dashboard (Main Page)
- **Header**: Logo, navigation, user menu, theme toggle
- **Stats Cards**: Total analyses, success rate, processing time
- **Recent Activity**: Last 10 analyses with status
- **Quick Actions**: "New Analysis" button, "Batch Upload" button

### 3. Single Analysis Page
- **Input Form**: 
  - URL input with validation
  - Profile type selector (Software, Fintech, Edtech, Healthtech)
  - Submit button with loading state
- **Results Display**:
  - Classification result with confidence score
  - Processing time
  - AI comment/explanation
  - Raw data expandable section
- **History**: Previous analyses for same domain

### 4. Batch Analysis Page
- **Upload Interface**: 
  - CSV file upload with drag & drop
  - URL list input (textarea)
  - Progress tracking with real-time updates
- **Session Management**:
  - Active sessions list
  - Progress bars per session
  - Cancel/pause functionality
- **Results Table**: 
  - Sortable columns
  - Filter by status, profile type
  - Export to CSV

### 5. Results & History Page
- **Search & Filters**: 
  - Search by domain/URL
  - Filter by date, profile type, status
  - Sort options
- **Data Table**: 
  - Pagination
  - Bulk actions (export, delete)
  - Row details modal
- **Analytics**: 
  - Charts showing analysis trends
  - Success rate over time
  - Profile type distribution

### 6. Admin Panel (Role-based)
- **Prompt Management**: 
  - CRUD operations for AI prompts
  - Set default prompts per profile type
  - Version history
- **User Management**: 
  - User list with roles
  - Activity monitoring
- **System Settings**: 
  - API configuration
  - Rate limits
  - System health

## Design System

### Color Palette
**Light Theme:**
- Primary: #3B82F6 (Blue)
- Secondary: #6366F1 (Indigo)
- Success: #10B981 (Emerald)
- Warning: #F59E0B (Amber)
- Error: #EF4444 (Red)
- Background: #FFFFFF, #F8FAFC
- Text: #1F2937, #6B7280
- Border: #E5E7EB

**Dark Theme:**
- Primary: #60A5FA (Light Blue)
- Secondary: #818CF8 (Light Indigo)
- Success: #34D399 (Light Emerald)
- Warning: #FBBF24 (Light Amber)
- Error: #F87171 (Light Red)
- Background: #111827, #1F2937
- Text: #F9FAFB, #D1D5DB
- Border: #374151

### Typography
- **Font Family**: Inter, system-ui, sans-serif
- **Headings**: 
  - H1: 2.25rem (36px), font-weight: 700
  - H2: 1.875rem (30px), font-weight: 600
  - H3: 1.5rem (24px), font-weight: 600
- **Body**: 1rem (16px), font-weight: 400
- **Small**: 0.875rem (14px), font-weight: 400

### Components

#### Buttons
- **Primary**: Solid background, white text, rounded-lg, px-4 py-2
- **Secondary**: Border only, primary color text, rounded-lg, px-4 py-2
- **Ghost**: No border, primary color text, hover background
- **Danger**: Red background/text for destructive actions
- **Loading**: Spinner + disabled state

#### Forms
- **Input Fields**: 
  - Rounded borders, focus ring
  - Label above input
  - Error states with red border + message
  - Placeholder text
- **Select Dropdowns**: Custom styled, searchable
- **File Upload**: Drag & drop zone with preview
- **Textarea**: Resizable, character count

#### Cards
- **Elevated**: Shadow, rounded corners, padding
- **Outlined**: Border only, no shadow
- **Interactive**: Hover effects, clickable

#### Tables
- **Headers**: Bold, sortable indicators
- **Rows**: Hover effects, alternating colors
- **Pagination**: Page numbers, prev/next
- **Empty State**: Illustration + message

#### Status Indicators
- **Badges**: 
  - Success: Green background
  - Warning: Yellow background
  - Error: Red background
  - Info: Blue background
- **Progress Bars**: Animated, percentage display
- **Loading Spinners**: Centered, various sizes

#### Modals & Overlays
- **Backdrop**: Semi-transparent overlay
- **Content**: Centered, max-width, scrollable
- **Close**: X button, ESC key, click outside
- **Actions**: Buttons aligned right

### Layout & Spacing
- **Container**: Max-width 1200px, centered
- **Grid**: CSS Grid for complex layouts
- **Spacing**: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- **Responsive**: Mobile-first, breakpoints at 640px, 768px, 1024px, 1280px

### Animations & Transitions
- **Hover**: 150ms ease-in-out
- **Focus**: 200ms ease-in-out
- **Page Transitions**: 300ms ease-in-out
- **Loading**: Subtle pulse, fade in/out
- **Success/Error**: Slide in from top

## Technical Requirements

### Framework & Libraries
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Hook Form** for form handling
- **React Query** for data fetching
- **Framer Motion** for animations
- **Lucide React** for icons

### State Management
- **Context API** for theme switching
- **Local Storage** for theme persistence
- **React Query** for server state
- **Zustand** for complex client state (optional)

### Mock Data Structure
```typescript
// Analysis Result
interface AnalysisResult {
  id: string;
  domain: string;
  url: string;
  profile_type: 'software' | 'fintech' | 'edtech' | 'healthtech';
  classification: string;
  confidence: number;
  comment: string;
  processing_time: number;
  status: 'completed' | 'processing' | 'failed';
  created_at: string;
  raw_data: object;
}

// Batch Session
interface BatchSession {
  id: string;
  name: string;
  total_domains: number;
  completed: number;
  failed: number;
  status: 'active' | 'completed' | 'paused' | 'failed';
  created_at: string;
  updated_at: string;
}
```

### API Integration Points (Mock for now)
```typescript
// Mock API functions - replace with real calls later
const api = {
  analyze: (url: string, profileType: string) => Promise<AnalysisResult>,
  analyzeBatch: (domains: string[]) => Promise<BatchSession>,
  getResults: (filters?: object) => Promise<AnalysisResult[]>,
  getSession: (sessionId: string) => Promise<BatchSession>,
  // ... other endpoints
};
```

## User Experience Guidelines

### Navigation
- **Top Navigation**: Logo, main pages, user menu
- **Breadcrumbs**: For deep navigation
- **Sidebar**: Collapsible for admin features
- **Mobile**: Hamburger menu, bottom navigation

### Feedback & Notifications
- **Toast Messages**: Success, error, info notifications
- **Loading States**: Skeleton screens, progress indicators
- **Error Handling**: User-friendly error messages
- **Empty States**: Helpful illustrations and CTAs

### Accessibility
- **Keyboard Navigation**: Tab order, shortcuts
- **Screen Readers**: ARIA labels, semantic HTML
- **Color Contrast**: WCAG AA compliance
- **Focus Indicators**: Visible focus rings

### Performance
- **Lazy Loading**: Route-based code splitting
- **Image Optimization**: WebP format, lazy loading
- **Bundle Size**: Tree shaking, minimal dependencies
- **Caching**: Service worker for offline capability

## Implementation Notes

1. **Start with**: Authentication pages, dashboard layout
2. **Theme System**: Use CSS variables for easy switching
3. **Responsive**: Mobile-first approach
4. **Mock Data**: Use realistic sample data
5. **Error Boundaries**: Catch and display errors gracefully
6. **Testing**: Unit tests for critical components

## Deliverables
- Complete React application with all pages
- Responsive design (mobile, tablet, desktop)
- Dark/light theme switching
- Mock data integration
- Clean, maintainable code structure
- README with setup instructions

Focus on creating a polished, professional interface that feels modern and scientific. The app should be intuitive for researchers while maintaining a sophisticated appearance.
