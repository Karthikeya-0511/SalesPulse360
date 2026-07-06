import axios from "axios";

const api = axios.create({
    baseURL: "https://salespulse360-backend.onrender.com",
});

export default api;