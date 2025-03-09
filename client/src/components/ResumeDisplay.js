import React from "react";
import { Button } from "./Button"; 
import { Card, CardContent, CardHeader, CardTitle } from "./Card"; 
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm"; 
import rehypeRaw from "rehype-raw";

const ResumeDisplay = ({ resumes, currentIndex, setCurrentIndex }) => {
    if (!resumes || resumes.length === 0 || !resumes[currentIndex]) {
        return <p className="text-gray-500 dark:text-gray-300">No resumes available.</p>;
    }

    const currentResume = resumes[currentIndex];

    return (
        <div className="mt-10 w-full max-w-7xl flex flex-col items-center px-6">
            {/* Title: Ranked by Score */}
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-6 text-center">
                Ranked by Score of Match
            </h2>

            {/* Candidate Info */}
            <div className="bg-blue-600 text-white py-3 px-6 rounded-lg text-lg font-medium mb-6 w-full text-center">
                Candidate {currentIndex + 1} of {resumes.length} | 
                <span className="ml-3"> <strong>Filename:</strong> {currentResume.filename} </span> | 
                <span className="ml-3"> <strong>Score:</strong> {Math.round(currentResume.score * 100)}% </span>
            </div>

            {/* Resume Comparison Section */}
            <div className="flex flex-row space-x-8 w-full">
                {/* Original Resume */}
                <Card className="w-1/2 p-6 shadow-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold text-center">Original Resume</CardTitle>
                    </CardHeader>
                    <CardContent className="overflow-auto max-h-[75vh]">
                        <div className="prose dark:prose-invert max-w-full whitespace-pre-wrap break-words">
                            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                                {currentResume.original_resume || "No resume found."}
                            </ReactMarkdown>
                        </div>
                    </CardContent>
                </Card>

                {/* Optimized Resume */}
                <Card className="w-1/2 p-6 shadow-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold text-center">Optimized Resume</CardTitle>
                    </CardHeader>
                    <CardContent className="overflow-auto max-h-[75vh]">
                        <div className="prose dark:prose-invert max-w-full whitespace-pre-wrap break-words">
                            <ReactMarkdown 
                                remarkPlugins={[remarkGfm]} 
                                rehypePlugins={[rehypeRaw]}
                                components={{
                                    p: ({ node, ...props }) => <p className="mb-2" {...props} />, // Adds spacing between paragraphs
                                    ul: ({ node, ...props }) => <ul className="list-disc ml-5" {...props} />, // Deals with bullet points
                                    ol: ({ node, ...props }) => <ol className="list-decimal ml-5" {...props} />, // Deals with numbered lists
                                    strong: ({ node, ...props }) => <strong className="font-bold text-gray-900 dark:text-gray-100" {...props} /> // Deals with bold
                                }}
                            >
                                {currentResume.optimized_resume || "No optimized resume available."}
                            </ReactMarkdown>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Navigation & Download Buttons */}
            <div className="flex justify-between w-full max-w-lg mt-8">
                <Button 
                    onClick={() => setCurrentIndex((prev) => Math.max(prev - 1, 0))}
                    disabled={currentIndex === 0}
                >
                    Previous
                </Button>
                {/* Download Button */}
                <Button as="a" href={`/download/${currentResume.filename}`} download className="mt-6">
                    Download Optimized Resume
                </Button>
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
