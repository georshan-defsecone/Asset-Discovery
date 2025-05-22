import MainPage from "./pages/mainPage"
import Scan from "./pages/Scan"
import Projects from "./pages/projects"
import AssetDetail from "./pages/AssetDetail"
const Router = [
    {
        path:"/projects/:project_name/assets/:asset_name",
        element:<AssetDetail/>
    },
    {
        path:"/scan",
        element:<Scan/>
    }
    ,
    {
        path:"/",
        element:<Projects/>
    },
     {
    path: "/projects/:projectName",
    element: <MainPage />,
  },
]

export default Router