import api from "./api";

export const startPipeline = async () => {
    const response = await api.post("/pipeline/start");
    return response.data;
};

export const stopPipeline = async () => {
    const response = await api.post("/pipeline/stop");
    return response.data;
};


export const getPipelineStatus = async () => {
    const response = await api.get("/pipeline/status");
    return response.data;
};