import { useNavigate } from "react-router-dom";

export const useNavigation = () => {
  const navigate = useNavigate();

  const handleResearcherClick = (researcherId: string) => {
    navigate(`/researcher/${researcherId}`);
  };

  return {
    handleResearcherClick,
    navigate,
  };
};