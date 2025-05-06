export interface FoodTruck {
    applicant: string;
    address: string;
    status: string;
    latitude: number;
    longitude: number;
    distance?: number;
}

export interface SearchCoordinates {
    latitude: number;
    longitude: number;
    includeAllStatuses: boolean;
} 