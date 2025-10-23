
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Outlet } from "react-router-dom";
import Layout from "@/components/Layout";
import { LayoutProvider } from "@/contexts/LayoutContext";
import Index from "./pages/Index";
import Researcher from "./pages/Researcher";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Componente Layout wrapper que renderiza o layout e o conteúdo das rotas filhas
const LayoutWrapper = () => (
  <LayoutProvider>
    <Layout>
      <Outlet />
    </Layout>
  </LayoutProvider>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LayoutWrapper />}>
            <Route index element={<Index />} />
            <Route path="researcher/:id" element={<Researcher />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
