import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import Layout from "@/components/Layout";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <Layout>
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4 text-slate-800">404</h1>
          <p className="text-xl text-slate-600 mb-4">Oops! Página não encontrada</p>
          <p className="text-slate-500 mb-6">A página que você está procurando não existe.</p>
        </div>
      </div>
    </Layout>
  );
};

export default NotFound;
