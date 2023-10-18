import { Stack } from "expo-router";
export default function Layout() {
  return (
    <Stack
      screenOptions={{
        headerTitle: "Library",
        headerStyle: {
        },
        headerTintColor: "#000",
        headerTitleStyle: {
          fontWeight: "bold",
        },
      }}
    />
  );
}