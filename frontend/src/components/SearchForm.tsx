import React, { useState } from 'react';

interface SearchFormProps {
    onSearchByName: (name: string, status?: string) => void;
    onSearchByAddress: (address: string) => void;
    onSearchNearest: (latitude: number, longitude: number, includeAllStatuses: boolean) => void;
    onClearResults: () => void;
}

export const SearchForm: React.FC<SearchFormProps> = ({
    onSearchByName,
    onSearchByAddress,
    onSearchNearest,
    onClearResults,
}) => {
    const [searchType, setSearchType] = useState<'name' | 'address' | 'nearest'>('name');
    const [name, setName] = useState('');
    const [status, setStatus] = useState<string>('');  // Empty string means no status selected
    const [address, setAddress] = useState('');
    const [latitude, setLatitude] = useState('');
    const [longitude, setLongitude] = useState('');
    const [includeAllStatuses, setIncludeAllStatuses] = useState(false);

    const handleSearchTypeChange = (type: 'name' | 'address' | 'nearest') => {
        setSearchType(type);
        onClearResults();
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        switch (searchType) {
            case 'name':
                onSearchByName(name, status || undefined);
                break;
            case 'address':
                onSearchByAddress(address);
                break;
            case 'nearest':
                onSearchNearest(
                    parseFloat(latitude),
                    parseFloat(longitude),
                    includeAllStatuses
                );
                break;
        }
    };

    return (
        <form onSubmit={handleSubmit} className="search-form">
            <div className="search-type-selector">
                <button
                    type="button"
                    onClick={() => handleSearchTypeChange('name')}
                    className={searchType === 'name' ? 'active' : ''}
                >
                    Search by Name
                </button>
                <button
                    type="button"
                    onClick={() => handleSearchTypeChange('address')}
                    className={searchType === 'address' ? 'active' : ''}
                >
                    Search by Address
                </button>
                <button
                    type="button"
                    onClick={() => handleSearchTypeChange('nearest')}
                    className={searchType === 'nearest' ? 'active' : ''}
                >
                    Nearest 5 Trucks
                </button>
            </div>

            {searchType === 'name' && (
                <div className="search-name">
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Enter food truck name"
                        required
                    />
                    <select
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        className="status-select"
                    >
                        <option value="">All Statuses</option>
                        <option value="APPROVED">Approved</option>
                        <option value="REQUESTED">Requested</option>
                        <option value="EXPIRED">Expired</option>
                    </select>
                </div>
            )}

            {searchType === 'address' && (
                <input
                    type="text"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="Enter street name"
                    required
                />
            )}

            {searchType === 'nearest' && (
                <>
                    <div className="search-nearest">
                        <input
                            type="number"
                            value={latitude}
                            onChange={(e) => setLatitude(e.target.value)}
                            placeholder="Latitude"
                            required
                            step="any"
                        />
                        <input
                            type="number"
                            value={longitude}
                            onChange={(e) => setLongitude(e.target.value)}
                            placeholder="Longitude"
                            required
                            step="any"
                        />
                    </div>
                    <label>
                        <input
                            type="checkbox"
                            checked={includeAllStatuses}
                            onChange={(e) => setIncludeAllStatuses(e.target.checked)}
                        />
                        Include all statuses
                    </label>
                </>
            )}

            <button type="submit">Search</button>
        </form>
    );
}; 