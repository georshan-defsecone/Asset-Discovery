import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import Header from "@/components/ui/header";
import Sidebar from "@/components/ui/sidebar";
import { Download } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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

  const handleDownload = async (projectName: string) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:80/projects/${projectName}/download`,
        {
          responseType: "blob",
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${projectName}_report.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert("Failed to download report.");
    }
  };

  return (
    <div>
      <Sidebar />
      <div className="ml-64">
        <Header />
        <main className="p-6 mt-16 min-h-screen bg-gray-100">
          <div className="max-w-4xl mx-auto bg-white shadow-lg ml-25 mt-15 rounded-md p-6 mt-5">
            <div className="mb-6 text-center">
              <h1 className="text-2xl font-bold text-gray-800">Available Projects</h1>
            </div>

            {error && <div className="text-red-600 mb-4 text-center">{error}</div>}

            {projects.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-3/4 text-left">Project Name</TableHead>
                    <TableHead className="w-1/4 text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {projects.map((project, index) => {
                    const projectName = project.replace(".db", "");
                    return (
                      <Link
                        key={index}
                        to={`/projects/${projectName}`}
                        className="contents"
                      >
                        <TableRow className="hover:bg-gray-100 cursor-pointer transition">
                          <TableCell className="w-3/4 text-left font-medium text-black">
                            {projectName}
                          </TableCell>
                          <TableCell
                            className="w-1/4 text-right"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <button
                              className="text-gray-600 hover:text-black transition"
                              title="Download project"
                              onClick={(e) => {
                                e.preventDefault(); // Prevent <Link> navigation
                                handleDownload(projectName);
                              }}
                            >
                              <Download className="w-5 h-5" />
                            </button>
                          </TableCell>
                        </TableRow>
                      </Link>
                    );
                  })}
                </TableBody>
              </Table>
            ) : (
              !error && <p className="text-center text-gray-600">No projects found.</p>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Projects;
