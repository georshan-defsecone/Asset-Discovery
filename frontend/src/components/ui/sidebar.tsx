import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <div className="fixed top-16 left-0 h-screen w-64 flex flex-col p-6 justify-between z-10 bg-white shadow-lg">
      <div>
        <h1 className="text-2xl font-semibold mb-8 text-gray-800">Dashboard</h1>
        <nav className="space-y-4">
          <Link
            to="/"
            className="block bg-gray-100 hover:bg-blue-100 text-gray-800 hover:text-blue-700 font-medium text-base px-4 py-2 rounded-md shadow-sm transition-all"
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
