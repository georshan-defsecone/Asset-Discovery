import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="w-screen fixed top-0 left-0 z-50 px-6 py-4 bg-gray-800 text-white flex items-center justify-between  shadow-md">
      <div></div>
      <h1 className="text-3xl font-extrabold text-white">Asset Discovery</h1>
      <Link
        to="/scan"
        className="px-4 py-2 bg-white text-black font-semibold text-sm font-sans border border-gray-300 rounded-md hover:bg-gray-100 transition-colors"
      >
        New Scan
      </Link>
    </header>
  );
};

export default Header;
