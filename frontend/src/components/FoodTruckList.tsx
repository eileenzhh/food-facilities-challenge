import React from 'react';
import { FoodTruck } from '../types/FoodTruck';

interface FoodTruckListProps {
    trucks: FoodTruck[];
    loading?: boolean;
    error?: string;
    hasSearched?: boolean;
}

export const FoodTruckList: React.FC<FoodTruckListProps> = ({ 
    trucks, 
    loading, 
    error,
    hasSearched = false
}) => {
    if (loading) return <div className="loading">Loading...</div>;
    if (error) return <div className="error">Error: {error}</div>;
    if (hasSearched && !trucks.length) return <div>No food trucks found</div>;

    return (
        <div className="food-truck-list">
            {trucks.map((truck, index) => (
                <div key={index} className="food-truck-card">
                    <h3>{truck.applicant}</h3>
                    <p>Address: {truck.address}</p>
                    <p>Status: {truck.status}</p>
                    {truck.distance && (
                        <p>Distance: {truck.distance.toFixed(2)} miles</p>
                    )}
                </div>
            ))}
        </div>
    );
}; 