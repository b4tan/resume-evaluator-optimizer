import React from "react";
import DownloadButton from "./Download";
import { Button } from "./Button"; 
import Markdown from "react-markdown";
import { Card, CardContent, CardHeader, CardTitle } from "./Card"; 

const ResumeDisplay = ({ resumes, currentIndex, setCurrentIndex }) => {
    // Sanity checks
    if (!resumes || resumes.length === 0 || !resumes[currentIndex]) {
        return <p className="text-gray-500 dark:text-gray-300">No resumes available.</p>;
    }

    const currentResume = resumes[currentIndex];

    return (
        <div className="mt-10 w-full max-w-6xl flex flex-col items-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                Ranked by Score of Match
            </h2>

            {/* Metadata display */}
            <p className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-5">
                Candidate {currentIndex + 1} of {resumes.length} | 
                <span className="ml-3 font-normal"> <strong>Filename:</strong> {currentResume.filename} </span> | 
                <span className="ml-3 font-normal"> <strong>Score:</strong> {Math.round(currentResume.score * 100)}% </span>
            </p>

            {/* Evaluation */}
            <div className="w-full mt-2 mb-8">
                <Card className="p-6 shadow-lg border border-gray-600">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold text-center">Evaluation</CardTitle>
                        <p className="text-center text-sm font-light text-gray-200 mb-5">Model has autonomy to create improvements and evaluates based on past data </p>
                    </CardHeader>
                    <CardContent className="p-3 border border-gray-600 overflow-auto max-h-[50vh] rounded-lg">
                        <div className="whitespace-pre-wrap break-words leading-tight scrollbar-hidden">
                            <Markdown>
                                {currentResume.evaluation ?? "No evaluation available."}
                            </Markdown>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Resume Comparison Section */}
            <div className="flex flex-row space-x-8 w-full">
                {/* Original Resume */}
                <Card className="w-1/2 p-6 shadow-lg border border-gray-600">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold">Original Resume</CardTitle>
                    </CardHeader>
                    <CardContent className="p-3 border border-gray-600 rounded-lg overflow-auto max-h-[70vh]">
                        <div className="whitespace-pre-wrap break-words leading-relaxed scrollbar-hidden">
                            {currentResume.original_resume ?? "No original resume available."}
                        </div>
                    </CardContent>
                </Card>

                {/* Optimized Resume */}
                <Card className="w-1/2 p-6 shadow-lg border border-gray-600">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold">Optimized Resume</CardTitle>
                    </CardHeader>
                    <CardContent className="p-3 border border-gray-600 rounded-lg overflow-auto max-h-[70vh]">
                        <div className="whitespace-pre-wrap break-words leading-relaxed scrollbar-hidden">
                            <Markdown>
                            {currentResume.optimized_resume ?? "No optimized resume available."}
                            </Markdown>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Navigation & Download Buttons */}
            <div className="flex justify-between w-full max-w-lg mt-8">
                {/* Prev Button */}
                <Button 
                    onClick={() => setCurrentIndex((prev) => Math.max(prev - 1, 0))}
                    disabled={currentIndex === 0}
                >
                    Prev
                </Button>

                {/* Download Button */}
                <DownloadButton filename={currentResume.filename} />
                
                {/* Next Button */}
                <Button 
                    onClick={() => setCurrentIndex((prev) => Math.min(prev + 1, resumes.length - 1))}
                    disabled={currentIndex >= resumes.length - 1}
                >
                    Next
                </Button>
            </div>
        </div>
    );
};

export default ResumeDisplay;
