import { FoodTruck, SearchCoordinates } from '../types/FoodTruck';

const API_BASE_URL = 'http://localhost:8000';

export const searchByName = async (name: string, status?: string): Promise<FoodTruck[]> => {
    const url = new URL(`${API_BASE_URL}/search/name/${encodeURIComponent(name)}`);
    if (status) {
        url.searchParams.append('status', status);
    }
    const response = await fetch(url.toString());
    if (!response.ok) throw new Error('Failed to search by name');
    return response.json();
};

export const searchByAddress = async (address: string): Promise<FoodTruck[]> => {
    const response = await fetch(`${API_BASE_URL}/search/address/${encodeURIComponent(address)}`);
    if (!response.ok) throw new Error('Failed to search by address');
    return response.json();
};

export const findNearest = async (coordinates: SearchCoordinates): Promise<FoodTruck[]> => {
    const response = await fetch(`${API_BASE_URL}/search/nearest`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(coordinates),
    });
    if (!response.ok) throw new Error('Failed to fetch nearest food trucks');
    return response.json();
}; 