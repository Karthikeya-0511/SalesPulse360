import api from "./api";

export const getActivity = async () => {
    const response = await api.get("/activity");
    return response.data;
};