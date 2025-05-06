import React, { useState } from 'react';
import { FoodTruck } from './types/FoodTruck';
import { SearchForm } from './components/SearchForm';
import { FoodTruckList } from './components/FoodTruckList';
import { searchByName, searchByAddress, findNearest } from './services/api';

function App() {
    const [trucks, setTrucks] = useState<FoodTruck[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [hasSearched, setHasSearched] = useState(false);

    const handleSearchByName = async (name: string, status?: string) => {
        try {
            setLoading(true);
            setError(null);
            const results = await searchByName(name, status);
            setTrucks(results);
            setHasSearched(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleSearchByAddress = async (address: string) => {
        try {
            setLoading(true);
            setError(null);
            const results = await searchByAddress(address);
            setTrucks(results);
            setHasSearched(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleSearchNearest = async (
        latitude: number,
        longitude: number,
        includeAllStatuses: boolean
    ) => {
        try {
            setLoading(true);
            setError(null);
            const results = await findNearest({
                latitude,
                longitude,
                includeAllStatuses,
            });
            setTrucks(results);
            setHasSearched(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleClearResults = () => {
        setTrucks([]);
        setError(null);
        setHasSearched(false);
    };

    return (
        <div className="app">
            <header>
                <h1>San Francisco Food Trucks</h1>
                <h2 className="subtitle">Support your local food trucks!</h2>
            </header>
            <main>
                <SearchForm
                    onSearchByName={handleSearchByName}
                    onSearchByAddress={handleSearchByAddress}
                    onSearchNearest={handleSearchNearest}
                    onClearResults={handleClearResults}
                />
                <FoodTruckList
                    trucks={trucks}
                    loading={loading}
                    error={error || undefined}
                    hasSearched={hasSearched}
                />
            </main>
        </div>
    );
}

export default App; 