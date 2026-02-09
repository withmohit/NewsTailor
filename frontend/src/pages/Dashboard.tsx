import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <main className="container mx-auto flex flex-col items-center px-4 py-24 text-center">
        <h1 className="text-3xl font-bold">Welcome back!</h1>
        <p className="mt-2 text-muted-foreground">
          Your personalised news feed will appear here once the backend is connected.
        </p>
        {/* TODO: Display user's selected categories and news feed here */}
      </main>
      <Footer />
    </div>
  );
};

export default Dashboard;
