import axios from 'axios';

const API_base_URL = '/api';

export const queryBackend = async (query) => {
    try {
        const response = await axios.post(`${API_base_URL}/query`, {
            query: query,
            top_k: 5
        });
        return response.data;
    } catch (error) {
        console.error("Error querying backend:", error);
        throw error;
    }
};
