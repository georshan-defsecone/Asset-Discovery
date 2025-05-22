import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Router from './router.tsx'
import './index.css'
import App from './App.tsx'

const routes = createBrowserRouter(Router)

createRoot(document.getElementById('root')!).render(
  <RouterProvider router={routes}></RouterProvider>
)
