import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<string[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:80/projects");
        setProjects(response.data.projects);
      } catch (err) {
        setError("Failed to fetch projects.");
      }
    };

    fetchProjects();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-10 px-4">
      <div className="max-w-3xl mx-auto bg-white shadow-lg rounded-md p-6 relative">
        {/* Title and New Button */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Available Projects</h2>
          <Link
            to="/scan"
            className="bg-neutral-800 text-white px-4 py-2 text-sm rounded hover:bg-gray-600 transition"
          >
            New
          </Link>
        </div>

        {/* Error Display */}
        {error && (
          <div className="text-red-600 mb-4">
            {error}
          </div>
        )}

        {/* Project List */}
        {projects.length > 0 ? (
          <ul className="space-y-2">
            {projects.map((project, index) => {
              const projectName = project.replace(".db", "");
              return (
                <li
                  key={index}
                  className="bg-gray-100 border border-gray-300 px-4 py-2 rounded"
                >
                  <Link
                    to={`/projects/${projectName}`}
                    className="text-black no-underline hover:underline"
                  >
                    {projectName}
                  </Link>
                </li>
              );
            })}
          </ul>
        ) : (
          !error && <p>No projects found.</p>
        )}
      </div>
    </div>
  );
};

export default Projects;
