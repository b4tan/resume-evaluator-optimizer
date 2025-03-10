import React from "react";
import { useNavigate } from "react-router-dom";

function Navbar() {
    const navigate = useNavigate();

    return (
        <nav className="bg-[#2f53bd] text-[#EEEBE3] shadow-md p-4 fixed w-full top-0 z-50 leading-relaxed">
            <div className="max-w-7xl mx-auto flex justify-center items-center">
                <h1 
                    className="text-2xl font-semibold cursor-pointer transition-transform duration-200 hover:scale-105"
                    onClick={() => navigate("/")}
                >
                    Agentic Resume Consulting
                </h1>
            </div>
        </nav>
    );
}

export default Navbar;
