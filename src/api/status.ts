import api from "./api";

export const getStatus = async () => {
    const response = await api.get("/status");
    return response.data;
};