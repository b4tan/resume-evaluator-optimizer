import React, { useState } from "react";
import axios from "axios";
import Navbar from "./Navbar";
import { Button } from "./components/button"; 
import { Textarea } from "./components/textarea"; 
import { Card, CardContent, CardHeader, CardTitle } from "./components/card"; 

function App() {
    const [resume, setResume] = useState(null);
    const [jobDesc, setJobDesc] = useState("");
    const [evaluation, setEvaluation] = useState("");
    const [optimizedResume, setOptimizedResume] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileChange = (event) => {
        setResume(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!resume) {
            alert("Please upload a resume.");
            return;
        }

        const formData = new FormData();
        formData.append("resume", resume);
        formData.append("job_description", jobDesc);
        formData.append("max_iterations", 5);

        setLoading(true);

        try {
            const response = await axios.post("http://127.0.0.1:8000/process/", formData);
            setEvaluation(response.data.evaluation.replace(/\n/g, "<br>"));
            setOptimizedResume(response.data.optimized_resume.replace(/\n/g, "<br>"));
        } catch (error) {
            alert("Error processing the resume. Please try again.");
            console.error("Error:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            <Navbar />

            <div className="flex flex-col items-center justify-center py-20 px-6">
                <Card className="w-full max-w-md">
                    <CardHeader>
                        <CardTitle className="text-center font-light">Please upload your resume below</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">

                        <div className="flex flex-col items-center w-full">
                            <label className="flex items-center justify-center w-1/3 border border-gray-400 text-gray-400 px-4 py-2 rounded-md cursor-pointer text-sm">
                                Choose File
                                <input type="file" accept=".pdf,.txt" onChange={handleFileChange} className="hidden" />
                            </label>
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                                {resume ? resume.name : "No file chosen"}
                            </p>
                        </div>

                        <Textarea placeholder="Paste job description here..." rows="4" onChange={(e) => setJobDesc(e.target.value)} />

                        <Button onClick={handleUpload} className="w-full" disabled={loading}>
                            {loading ? "Processing..." : "Upload & Analyze"}
                        </Button>

                        {/* Loading Bar */}
                        {loading && (
                            <div className="flex justify-center mt-4">
                                <div className="h-8 w-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {loading && <p className="text-gray-500 dark:text-gray-300 mt-4">Analyzing resume, please wait...</p>}

                <div className="mt-6 w-full max-w-3xl space-y-6">
                    {evaluation && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-blue-700">Evaluation</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {evaluation.split("\n").map((line, index) => (
                                    <p key={index} className="text-gray-700 dark:text-gray-300">{line}</p>
                                ))}
                            </CardContent>
                        </Card>
                    )}

                    {optimizedResume && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-green-600">Optimized Resume</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {optimizedResume.split("\n").map((line, index) => (
                                    <p key={index} className="text-gray-700 dark:text-gray-300">{line}</p>
                                ))}
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;