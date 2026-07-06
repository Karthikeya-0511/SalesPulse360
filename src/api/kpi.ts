import api from "./api";

export const getKPIs = async () => {
    const response = await api.get("/kpis");
    return response.data;
};