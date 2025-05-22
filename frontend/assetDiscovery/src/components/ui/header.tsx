import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="w-screen fixed top-0 left-0 z-50 px-6 py-4 bg-gray-800 text-white flex items-center justify-between  shadow-md">
      <div></div>
      <h1 className="text-3xl font-extrabold text-white">Asset Discovery</h1>
      <Link
        to="/scan"
        className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-blue-700 transition-colors"
      >
        New
      </Link>
    </header>
  );
};

export default Header;
