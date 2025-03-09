import React, { useState, useEffect } from "react";
import axios from "axios";
import Navbar from "./components/Navbar";
import UploadResume from "./components/UploadResume";  
import ResumeDisplay from "./components/ResumeDisplay";  

function App() {
    const [resumes, setResumes] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchRankedResumes();
    }, []);

    const fetchRankedResumes = async () => {
        setLoading(true);
        try {
            const response = await axios.get("http://127.0.0.1:8000/get_ranked_resumes/");
            if (response.data.resumes.length > 0) {
                setResumes(response.data.resumes); 
                setCurrentIndex(0);
            }
        } catch (error) {
            console.error("Error fetching resumes:", error);
        }
        setLoading(false);
    };
    

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            <Navbar />

            <div className="flex flex-col items-center justify-center py-20 px-6">
                {/* Upload Component */}
                <UploadResume onUploadComplete={fetchRankedResumes} />

                {/* Loading Indicator */}
                {loading && <p className="text-gray-500 dark:text-gray-300 mt-4">Loading resumes...</p>}

                {/* Resume Display Component */}
                {!loading && resumes.length > 0 && ( 
                    <ResumeDisplay
                        resumes={resumes}
                        currentIndex={currentIndex}
                        setCurrentIndex={setCurrentIndex}
                    />
                )}
            </div>
        </div>
    );
}

export default App;
