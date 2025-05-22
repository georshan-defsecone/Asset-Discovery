import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <div className="fixed top-16 left-0 h-screen w-64 flex flex-col p-6 justify-between z-10 bg-white shadow-lg">
      <div>
        <h1 className="text-2xl font-bold mb-8">Dashboard</h1>
        <nav className="space-y-4">
          <Link
            to="/"
            className="block text-lg text-gray-700 hover:text-blue-600 transition-colors"
          >
            Projects
          </Link>
        </nav>
      </div>
      <div className="text-sm text-gray-500">
        © {new Date().getFullYear()} Your Company
      </div>
    </div>
  );
};

export default Sidebar;
